"""
Clasificación de términos a partir de scores brutos.

Aplica umbrales, zonas grises y reglas de consenso para producir
una clasificación por término. No sabe cómo se calcularon los scores.

Prioridad de clasificación:
  1. EXACT       — match exacto con una voz conocida
  2. CONSENSUS   — >= min_votes por la misma entidad (+ Lev_OCR si requerido)
  3. WEAK        — >= 2 votos pero no cumple requisitos de CONSENSUS
  4. ONE_VOTE    — exactamente 1 voto
  5. GRAY_ZONE   — ningún voto pero al menos 1 en zona gris
  6. REJECTED    — sin coincidencias significativas
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from portada_s_index.config import ConsensusConfig


# ---------------------------------------------------------------------------
# Tipos de clasificación
# ---------------------------------------------------------------------------

Classification = Literal[
    "EXACT",
    "CONSENSUS",
    "WEAK",
    "SOME_VOTE",
    "GRAY_ZONE",
    "REJECTED",
]


# ---------------------------------------------------------------------------
# Dataclasses de resultado
# ---------------------------------------------------------------------------

@dataclass
class AlgorithmScore:
    """
    Score de un algoritmo concreto para un término.
    Parte del debug completo en el JSON de salida.
    """
    algorithm: str
    best_voice: str          # Voz de mayor score
    best_entity: str         # Entidad dueña de esa voz
    score: float
    threshold: float
    voted: bool              # score >= threshold
    in_gray_zone: bool       # gray_zone[0] <= score < threshold

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "best_voice": self.best_voice,
            "best_entity": self.best_entity,
            "score": round(self.score, 6),
            "threshold": self.threshold,
            "voted": self.voted,
            "in_gray_zone": self.in_gray_zone,
        }


@dataclass
class TermResult:
    """
    Resultado completo para un término evaluado.
    Se serializa directamente como JSON de salida.
    """
    term: str
    frequency: int
    normalized: str
    exact_match: bool

    classification: Classification
    entity: str              # Entidad asignada ("" si GRAY_ZONE o REJECTED)
    voice: str               # Voz concreta ganadora ("" si no hay consenso)
    votes: int               # Votos recibidos por la entidad ganadora

    algorithm_scores: list[AlgorithmScore] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "frequency": self.frequency,
            "normalized": self.normalized,
            "exact_match": self.exact_match,
            "classification": self.classification,
            "entity": self.entity,
            "voice": self.voice,
            "votes": self.votes,
            "algorithm_scores": [s.to_dict() for s in self.algorithm_scores],
        }


# ---------------------------------------------------------------------------
# Función de clasificación
# ---------------------------------------------------------------------------

def classify(
    term: str,
    frequency: int,
    normalized: str,
    scores: list[AlgorithmScore],
    consensus: ConsensusConfig,
    exact_match: bool,
    exact_entity: str = "",
    exact_voice: str = "",
) -> TermResult:
    """
    Clasifica un término a partir de sus scores por algoritmo.

    Args:
        term          : Término original (sin normalizar)
        frequency     : Frecuencia del término en el corpus
        normalized    : Término tras normalize()
        scores        : Lista de AlgorithmScore, uno por algoritmo activo
        consensus     : Configuración de consenso del pipeline
        exact_match   : True si el término normalizado existe como voz exacta
        exact_entity  : Entidad del match exacto (si exact_match=True)
        exact_voice   : Voz del match exacto (si exact_match=True)
    """

    # Prioridad 1: match exacto
    if exact_match:
        return TermResult(
            term=term,
            frequency=frequency,
            normalized=normalized,
            exact_match=True,
            classification="EXACT",
            entity=exact_entity,
            voice=exact_voice,
            votes=0,
            algorithm_scores=[],
        )

    # Contabilizar votos y detectar zona gris
    # votos_por_entidad: entidad → [(algoritmo, voz, score)]
    votos_por_entidad: dict[str, list[tuple[str, str, float]]] = {}
    en_zona_gris_por_entidad: dict[str, list[tuple[str, str, float]]] = {}
    en_zona_gris = False
    lev_ocr_vote_entity: str | None = None   # Entidad por la que votó Lev_OCR

    for s in scores:
        if s.voted:
            if s.best_entity not in votos_por_entidad:
                votos_por_entidad[s.best_entity] = []
            votos_por_entidad[s.best_entity].append((s.algorithm, s.best_voice, s.score))
            if s.algorithm == "levenshtein_ocr":
                lev_ocr_vote_entity = s.best_entity
        elif s.in_gray_zone:
            if s.best_entity not in en_zona_gris_por_entidad:
                en_zona_gris_por_entidad[s.best_entity] = []
            en_zona_gris_por_entidad[s.best_entity].append((s.algorithm, s.best_voice, s.score))
            en_zona_gris = True

    # Sin votos
    if not votos_por_entidad:
        classification: Classification = "GRAY_ZONE" if en_zona_gris else "REJECTED"
        winning_entity = max(en_zona_gris_por_entidad, key=lambda e: len(en_zona_gris_por_entidad[e])) if en_zona_gris else ""
        winning_voice = max(en_zona_gris_por_entidad[winning_entity], key=lambda x: x[2])[1] if en_zona_gris else ""
        return TermResult(
            term=term,
            frequency=frequency,
            normalized=normalized,
            exact_match=False,
            classification=classification,
            entity=winning_entity,
            voice=winning_voice,
            votes=0,
            algorithm_scores=scores,
        )

    # Entidad con más votos
    winning_entity = max(votos_por_entidad, key=lambda e: len(votos_por_entidad[e]))
    winning_votes_list = votos_por_entidad[winning_entity]
    winning_vote_count = len(winning_votes_list)
    total_votes = sum(len(v) for v in votos_por_entidad.values())
    total_en_zona_gris = sum(len(v) for v in en_zona_gris_por_entidad.values()) if en_zona_gris else 0

    # Determinar la voz ganadora:
    # Preferencia: la voz que votó Lev_OCR (si está en la entidad ganadora)
    winning_voice = ""
    lev_ocr_in_consensus = lev_ocr_vote_entity == winning_entity

    if lev_ocr_in_consensus:
        # Tomar la voz que Lev_OCR propuso
        for algo, voice, _ in winning_votes_list:
            if algo == "levenshtein_ocr":
                winning_voice = voice
                break
    if not winning_voice:
        # Tomar la voz con mayor score entre los votantes de la entidad ganadora
        best = max(winning_votes_list, key=lambda x: x[2])
        winning_voice = best[1]

    # Prioridad 2: CONSENSUS
    lev_ocr_ok = (not consensus.require_levenshtein_ocr) or lev_ocr_in_consensus
    if winning_vote_count >= consensus.min_votes and lev_ocr_ok:
        return TermResult(
            term=term,
            frequency=frequency,
            normalized=normalized,
            exact_match=False,
            classification="CONSENSUS",
            entity=winning_entity,
            voice=winning_voice,
            votes=winning_vote_count,
            algorithm_scores=scores,
        )

    # Prioridad 3: WEAK (votos suficientes pero sin cumplir Lev_OCR)
    if winning_vote_count >= consensus.min_votes :
        return TermResult(
            term=term,
            frequency=frequency,
            normalized=normalized,
            exact_match=False,
            classification="WEAK",
            entity=winning_entity,
            voice=winning_voice,
            votes=winning_vote_count,
            algorithm_scores=scores,
        )

    # Prioridad 4: ALMOST_AGREED
    if total_votes > total_en_zona_gris and total_votes >= consensus.min_votes//2:
        return TermResult(
            term=term,
            frequency=frequency,
            normalized=normalized,
            exact_match=False,
            classification="SOME_VOTE",
            entity=winning_entity,
            voice=winning_voice,
            votes=winning_vote_count,
            algorithm_scores=scores,
        )

    # Prioridad 5: GRAY_ZONE
    if en_zona_gris:
        winning_entity = max(en_zona_gris_por_entidad, key=lambda e: len(en_zona_gris_por_entidad[e]))
        winning_voice = max(en_zona_gris_por_entidad[winning_entity], key=lambda x: x[2])[1]
        return TermResult(
            term=term,
            frequency=frequency,
            normalized=normalized,
            exact_match=False,
            classification="GRAY_ZONE",
            entity=winning_entity,
            voice= winning_voice,
            votes=0,
            algorithm_scores=scores,
        )

    # Prioridad 6: REJECTED
    return TermResult(
        term=term,
        frequency=frequency,
        normalized=normalized,
        exact_match=False,
        classification="REJECTED",
        entity="",
        voice="",
        votes=0,
        algorithm_scores=scores,
    )