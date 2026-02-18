"""
Módulo principal de similitud con configuración y clasificación de términos.
"""

import re
import unicodedata
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Callable, Optional, Any
import json

from .algorithms import (
    levenshtein_ratio,
    levenshtein_ratio_ocr,
    jaro_winkler_similarity,
    ngram_similarity,
)


# =============================================================================
# ENUMERACIONES
# =============================================================================

class SimilarityAlgorithm(str, Enum):
    """Algoritmos de similitud disponibles."""
    LEVENSHTEIN_OCR = "levenshtein_ocr"
    LEVENSHTEIN_RATIO = "levenshtein_ratio"
    JARO_WINKLER = "jaro_winkler"
    NGRAM_2 = "ngram_2"
    NGRAM_3 = "ngram_3"


class ClassificationLevel(str, Enum):
    """Niveles de clasificación de nombres."""
    CONSENSUADO = "CONSENSUADO"
    CONSENSUADO_DEBIL = "CONSENSUADO_DEBIL"
    SOLO_1_VOTO = "SOLO_1_VOTO"
    ZONA_GRIS = "ZONA_GRIS"
    RECHAZADO = "RECHAZADO"


# =============================================================================
# MAPEO DE ALGORITMOS
# =============================================================================

ALGORITHM_FUNCTIONS: Dict[SimilarityAlgorithm, Callable[[str, str], float]] = {
    SimilarityAlgorithm.LEVENSHTEIN_OCR: levenshtein_ratio_ocr,
    SimilarityAlgorithm.LEVENSHTEIN_RATIO: levenshtein_ratio,
    SimilarityAlgorithm.JARO_WINKLER: jaro_winkler_similarity,
    SimilarityAlgorithm.NGRAM_2: lambda a, b: ngram_similarity(a, b, n=2),
    SimilarityAlgorithm.NGRAM_3: lambda a, b: ngram_similarity(a, b, n=3),
}

DEFAULT_THRESHOLDS: Dict[SimilarityAlgorithm, float] = {
    SimilarityAlgorithm.LEVENSHTEIN_OCR: 0.75,
    SimilarityAlgorithm.LEVENSHTEIN_RATIO: 0.75,
    SimilarityAlgorithm.JARO_WINKLER: 0.85,
    SimilarityAlgorithm.NGRAM_2: 0.66,
    SimilarityAlgorithm.NGRAM_3: 0.60,
}

DEFAULT_GRAY_ZONES: Dict[SimilarityAlgorithm, tuple[float, float]] = {
    SimilarityAlgorithm.LEVENSHTEIN_OCR: (0.71, 0.749),
    SimilarityAlgorithm.LEVENSHTEIN_RATIO: (0.71, 0.749),
    SimilarityAlgorithm.JARO_WINKLER: (0.80, 0.849),
    SimilarityAlgorithm.NGRAM_2: (0.63, 0.659),
    SimilarityAlgorithm.NGRAM_3: (0.55, 0.599),
}


# =============================================================================
# NORMALIZACIÓN DE TEXTO
# =============================================================================

def normalize_text(text: str) -> str:
    """
    Normaliza texto a forma canónica.
    
    Proceso:
    1. Descomposición Unicode (NFD)
    2. Eliminación de marcas diacríticas
    3. Conversión a minúsculas
    4. Eliminación de caracteres no alfabéticos (excepto espacios y guiones)
    5. Normalización de espacios múltiples
    
    Args:
        text: Texto a normalizar
    
    Returns:
        Texto normalizado
    """
    if not text:
        return ""
    
    # Descomponer y eliminar marcas diacríticas
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    
    # Minúsculas y limpieza
    lowered = without_marks.lower()
    cleaned = re.sub(r"[^a-z\s-]", " ", lowered)
    
    # Normalizar espacios
    return " ".join(cleaned.split())


# =============================================================================
# CLASES DE DATOS
# =============================================================================

@dataclass
class SimilarityConfig:
    """
    Configuración para el cálculo de similitud.
    
    Attributes:
        algorithms: Lista de algoritmos a usar
        thresholds: Umbrales de aprobación por algoritmo
        gray_zones: Zonas grises (piso, techo) por algoritmo
        normalize: Si se debe normalizar el texto antes de comparar
        min_votes_consensus: Votos mínimos para consenso (default: 2)
        require_levenshtein_ocr: Si Levenshtein OCR debe estar en consenso (default: True)
    """
    algorithms: List[SimilarityAlgorithm] = field(
        default_factory=lambda: [
            SimilarityAlgorithm.LEVENSHTEIN_OCR,
            SimilarityAlgorithm.JARO_WINKLER,
            SimilarityAlgorithm.NGRAM_2,
        ]
    )
    thresholds: Dict[SimilarityAlgorithm, float] = field(default_factory=dict)
    gray_zones: Dict[SimilarityAlgorithm, tuple[float, float]] = field(default_factory=dict)
    normalize: bool = True
    min_votes_consensus: int = 2
    require_levenshtein_ocr: bool = True
    
    def __post_init__(self):
        """Inicializa umbrales y zonas grises con valores por defecto si no se especifican."""
        for algo in self.algorithms:
            if algo not in self.thresholds:
                self.thresholds[algo] = DEFAULT_THRESHOLDS[algo]
            if algo not in self.gray_zones:
                self.gray_zones[algo] = DEFAULT_GRAY_ZONES[algo]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return {
            "algorithms": [algo.value for algo in self.algorithms],
            "thresholds": {algo.value: threshold for algo, threshold in self.thresholds.items()},
            "gray_zones": {algo.value: zone for algo, zone in self.gray_zones.items()},
            "normalize": self.normalize,
            "min_votes_consensus": self.min_votes_consensus,
            "require_levenshtein_ocr": self.require_levenshtein_ocr,
        }
    
    def to_json(self, **kwargs) -> str:
        """Convierte la configuración a JSON."""
        return json.dumps(self.to_dict(), **kwargs)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimilarityConfig":
        """Crea una configuración desde un diccionario."""
        algorithms = [SimilarityAlgorithm(algo) for algo in data.get("algorithms", [])]
        thresholds = {
            SimilarityAlgorithm(algo): threshold 
            for algo, threshold in data.get("thresholds", {}).items()
        }
        gray_zones = {
            SimilarityAlgorithm(algo): tuple(zone) 
            for algo, zone in data.get("gray_zones", {}).items()
        }
        
        return cls(
            algorithms=algorithms,
            thresholds=thresholds,
            gray_zones=gray_zones,
            normalize=data.get("normalize", True),
            min_votes_consensus=data.get("min_votes_consensus", 2),
            require_levenshtein_ocr=data.get("require_levenshtein_ocr", True),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "SimilarityConfig":
        """Crea una configuración desde JSON."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class SimilarityResult:
    """
    Resultado de comparación de similitud entre un término y una voz.
    
    Attributes:
        term: Término original
        voice: Voz comparada
        algorithm: Algoritmo usado
        similarity: Valor de similitud (0.0 a 1.0)
        approved: Si supera el umbral de aprobación
        in_gray_zone: Si está en zona gris
    """
    term: str
    voice: str
    algorithm: SimilarityAlgorithm
    similarity: float
    approved: bool
    in_gray_zone: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "term": self.term,
            "voice": self.voice,
            "algorithm": self.algorithm.value,
            "similarity": round(self.similarity, 4),
            "approved": self.approved,
            "in_gray_zone": self.in_gray_zone,
        }
    
    def to_json(self, **kwargs) -> str:
        """Convierte el resultado a JSON."""
        return json.dumps(self.to_dict(), **kwargs)


@dataclass
class TermClassification:
    """
    Clasificación completa de un nombre.
    
    Attributes:
        term: Nombre original
        frequency: Frecuencia de aparición
        results: Resultados por algoritmo
        votes_approval: Número de votos de aprobación
        entity_consensus: Entidad consensuada
        voice_consensus: Voz consensuada
        votes_entity: Votos para la entidad consensuada
        levenshtein_ocr_in_consensus: Si Levenshtein OCR votó por la entidad consensuada
        classification: Nivel de clasificación
    """
    term: str
    frequency: int
    results: Dict[SimilarityAlgorithm, SimilarityResult]
    votes_approval: int
    entity_consensus: str
    voice_consensus: str
    votes_entity: int
    levenshtein_ocr_in_consensus: bool
    classification: ClassificationLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la clasificación a diccionario."""
        results_dict = {}
        for algo, result in self.results.items():
            results_dict[algo.value] = {
                "similarity": round(result.similarity, 4),
                "voice": result.voice,
                "approved": result.approved,
                "in_gray_zone": result.in_gray_zone,
            }
        
        return {
            "term": self.term,
            "frequency": self.frequency,
            "results": results_dict,
            "votes_approval": self.votes_approval,
            "entity_consensus": self.entity_consensus,
            "voice_consensus": self.voice_consensus,
            "votes_entity": self.votes_entity,
            "levenshtein_ocr_in_consensus": self.levenshtein_ocr_in_consensus,
            "classification": self.classification.value,
        }
    
    def to_json(self, **kwargs) -> str:
        """Convierte la clasificación a JSON."""
        return json.dumps(self.to_dict(), **kwargs)


# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

def calculate_similarity(
    term: str,
    voices: List[str],
    config: Optional[SimilarityConfig] = None,
    voice_to_entity: Optional[Dict[str, str]] = None,
) -> Dict[SimilarityAlgorithm, SimilarityResult]:
    """
    Calcula la similitud de un nombre con una lista de voces usando múltiples algoritmos.
    
    Args:
        term: Nombre a comparar
        voices: Lista de voces de referencia
        config: Configuración de similitud (usa default si no se especifica)
        voice_to_entity: Mapeo de voz normalizada a entidad (opcional)
    
    Returns:
        Diccionario con resultados por algoritmo
    """
    if config is None:
        config = SimilarityConfig()
    
    if voice_to_entity is None:
        voice_to_entity = {}
    
    # Normalizar término si es necesario
    term_normalized = normalize_text(term) if config.normalize else term
    
    results = {}
    
    for algo in config.algorithms:
        # Calcular similitud con cada voz
        similarities = []
        for voice in voices:
            voice_normalized = normalize_text(voice) if config.normalize else voice
            func = ALGORITHM_FUNCTIONS[algo]
            sim = func(term_normalized, voice_normalized)
            similarities.append((sim, voice))
        
        # Obtener la mejor coincidencia
        if similarities:
            max_sim, best_voice = max(similarities, key=lambda x: x[0])
        else:
            max_sim, best_voice = 0.0, ""
        
        # Verificar aprobación y zona gris
        threshold = config.thresholds[algo]
        gray_floor, gray_ceiling = config.gray_zones[algo]
        
        approved = max_sim >= threshold
        in_gray_zone = gray_floor <= max_sim <= gray_ceiling
        
        results[algo] = SimilarityResult(
            term=term,
            voice=best_voice,
            algorithm=algo,
            similarity=max_sim,
            approved=approved,
            in_gray_zone=in_gray_zone,
        )
    
    return results


def classify_name(
    name: List[str],
    voices: List[str],
    frequencies: Optional[Dict[str, int]] = None,
    config: Optional[SimilarityConfig] = None,
    voice_to_entity: Optional[Dict[str, str]] = None,
) -> List[TermClassification]:
    """
    Clasifica una lista de términos según similitud con voces de referencia.
    
    Args:
        name: Lista de términos a clasificar
        voices: Lista de voces de referencia
        frequencies: Diccionario de frecuencias por término (opcional)
        config: Configuración de similitud (usa default si no se especifica)
        voice_to_entity: Mapeo de voz normalizada a entidad (opcional)
    
    Returns:
        Lista de clasificaciones de términos
    """
    if config is None:
        config = SimilarityConfig()
    
    if frequencies is None:
        frequencies = {term: 1 for term in name}
    
    if voice_to_entity is None:
        voice_to_entity = {}
    
    classifications = []
    
    for term in name:
        frequency = frequencies.get(term, 0)
        
        # Calcular similitudes
        results = calculate_similarity(term, voices, config, voice_to_entity)
        
        # Contar votos de aprobación
        votes_approval = sum(1 for result in results.values() if result.approved)
        
        # Verificar si hay algún resultado en zona gris
        in_gray_zone = any(result.in_gray_zone for result in results.values())
        
        # Determinar entidad consensuada
        votes_by_entity: Dict[str, List[tuple[SimilarityAlgorithm, str]]] = {}
        lev_ocr_voice = None
        
        for algo, result in results.items():
            if result.approved:
                voice_norm = normalize_text(result.voice) if config.normalize else result.voice
                entity = voice_to_entity.get(voice_norm, result.voice)
                
                if entity not in votes_by_entity:
                    votes_by_entity[entity] = []
                votes_by_entity[entity].append((algo, result.voice))
                
                if algo == SimilarityAlgorithm.LEVENSHTEIN_OCR:
                    lev_ocr_voice = result.voice
        
        # Entidad con más votos
        entity_consensus = ""
        voice_consensus = ""
        votes_entity = 0
        lev_ocr_in_consensus = False
        
        if votes_by_entity:
            entity_consensus = max(votes_by_entity, key=lambda e: len(votes_by_entity[e]))
            votes_entity = len(votes_by_entity[entity_consensus])
            algorithms_consensus = [algo for algo, _ in votes_by_entity[entity_consensus]]
            lev_ocr_in_consensus = SimilarityAlgorithm.LEVENSHTEIN_OCR in algorithms_consensus
            
            # Voz consensuada
            if lev_ocr_in_consensus and lev_ocr_voice:
                voice_consensus = lev_ocr_voice
            else:
                voice_consensus = votes_by_entity[entity_consensus][0][1]
        
        # Determinar clasificación
        if (
            votes_entity >= config.min_votes_consensus and
            (lev_ocr_in_consensus or not config.require_levenshtein_ocr)
        ):
            classification = ClassificationLevel.CONSENSUADO
        elif votes_approval >= config.min_votes_consensus:
            classification = ClassificationLevel.CONSENSUADO_DEBIL
        elif votes_approval == 1:
            classification = ClassificationLevel.SOLO_1_VOTO
        elif in_gray_zone:
            classification = ClassificationLevel.ZONA_GRIS
        else:
            classification = ClassificationLevel.RECHAZADO
        
        classifications.append(
            TermClassification(
                term=term,
                frequency=frequency,
                results=results,
                votes_approval=votes_approval,
                entity_consensus=entity_consensus,
                voice_consensus=voice_consensus,
                votes_entity=votes_entity,
                levenshtein_ocr_in_consensus=lev_ocr_in_consensus,
                classification=classification,
            )
        )
    
    return classifications
