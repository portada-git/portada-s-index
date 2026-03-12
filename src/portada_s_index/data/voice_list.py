"""
Lista de voces conocidas para un tipo de entidad.

VoiceList parsea el formato .txt jerárquico o un dict JSON,
normaliza las voces y construye un índice de bloqueo para
acelerar la búsqueda de candidatos.

Corresponde a VoiceRow, JsonVoice y UniqueTerm del diagrama de clases.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from portada_s_index.normalize import normalize


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------

class VoiceListParseError(ValueError):
    """El archivo .txt de voces tiene formato incorrecto."""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Voice:
    """
    Una variante conocida de una entidad.

    raw        : "bergantín"  — tal como está en el .txt
    normalized : "bergantin"  — tras normalize()
    entity     : "BERGANTIN"  — entidad padre
    """
    raw: str
    normalized: str
    entity: str


@dataclass(slots=True)
class UniqueTerm:
    """
    Un término único a evaluar.
    Corresponde a UniqueTerm del diagrama de clases.
    """
    value: str      # Valor normalizado


# ---------------------------------------------------------------------------
# VoiceList
# ---------------------------------------------------------------------------

class VoiceList:
    """
    Lista de entidades conocidas con sus variantes para un tipo de entidad.

    Construye internamente un índice de bloqueo por (prefijo_2, longitud)
    que reduce el espacio de comparación de O(N) a O(k) para algoritmos léxicos.
    """

    def __init__(self, entity_type: str, voices: list[Voice]) -> None:
        self.entity_type = entity_type
        self._voices = voices

        # Índice: voz_normalizada → entidad
        self._norm_to_entity: dict[str, str] = {
            v.normalized: v.entity for v in voices if v.normalized
        }

        # Índice de bloqueo: (prefijo_2, longitud) → [Voice, ...]
        self._block_index: dict[tuple[str, int], list[Voice]] = {}
        for voice in voices:
            norm = voice.normalized
            if not norm:
                continue
            prefix = norm[:2] if len(norm) >= 2 else norm
            key = (prefix, len(norm))
            if key not in self._block_index:
                self._block_index[key] = []
            self._block_index[key].append(voice)

    # ------------------------------------------------------------------
    # Constructores
    # ------------------------------------------------------------------

    @classmethod
    def from_txt(cls, entity_type: str, path: str | Path) -> "VoiceList":
        """
        Parsea el formato jerárquico .txt:

            BERGANTIN:
               - bergantín
               - bgn
               - berg.
            BOMBARDA:
               - bombarda
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Lista de voces no encontrada: {p}")

        voices: list[Voice] = []
        current_entity: str | None = None

        with open(p, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.rstrip()
                if not stripped.strip():
                    continue

                # Línea de entidad: "BERGANTIN:" (sin sangría, termina en ":")
                if stripped.strip().endswith(":") and not stripped.startswith(" "):
                    current_entity = stripped.strip()[:-1].strip()
                    continue

                # Línea de voz: "   - bergantín"
                if stripped.strip().startswith("-"):
                    if current_entity is None:
                        raise VoiceListParseError(
                            f"Línea {line_num}: voz encontrada antes de entidad: {stripped!r}"
                        )
                    raw = stripped.strip()[1:].strip()
                    if raw:
                        voices.append(Voice(
                            raw=raw,
                            normalized=normalize(raw),
                            entity=current_entity,
                        ))

        if not voices:
            raise VoiceListParseError(f"No se encontraron voces en: {p}")

        return cls(entity_type=entity_type, voices=voices)

    @classmethod
    def from_dict(cls, entity_type: str, data: dict[str, list[str]]) -> "VoiceList":
        """
        Construye desde un dict:
            {"BERGANTIN": ["bergantín", "bgn"], "BOMBARDA": ["bombarda"]}
        """
        voices: list[Voice] = []
        for entity, variants in data.items():
            for raw in variants:
                if raw:
                    voices.append(Voice(
                        raw=raw,
                        normalized=normalize(raw),
                        entity=entity,
                    ))
        return cls(entity_type=entity_type, voices=voices)

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def candidates_for(self, term: str, window: int = 2) -> list[Voice]:
        """
        Devuelve candidatos usando el índice de bloqueo.

        Busca voces cuya longitud esté en [len(term)-window, len(term)+window]
        y compartan el prefijo de 2 caracteres con el término.

        Si no hay candidatos con ese criterio, devuelve todas las voces
        (fallback para términos muy cortos o prefijos poco frecuentes).
        """
        norm = normalize(term)
        if not norm:
            return self._voices

        prefix = norm[:2] if len(norm) >= 2 else norm
        base_len = len(norm)
        candidates: list[Voice] = []

        for ln in range(max(1, base_len - window), base_len + window + 1):
            candidates.extend(self._block_index.get((prefix, ln), []))

        return candidates if candidates else self._voices

    def entity_of(self, normalized_voice: str) -> str:
        """Devuelve la entidad dueña de una voz normalizada, o "" si no existe."""
        return self._norm_to_entity.get(normalized_voice, "")

    def is_exact(self, normalized_term: str) -> bool:
        """True si el término normalizado existe directamente como voz."""
        return normalized_term in self._norm_to_entity

    @property
    def all_voices(self) -> list[Voice]:
        return list(self._voices)

    @property
    def all_normalized(self) -> list[str]:
        return [v.normalized for v in self._voices]

    @property
    def entities(self) -> list[str]:
        return sorted(set(v.entity for v in self._voices))

    def __len__(self) -> int:
        return len(self._voices)

    def __repr__(self) -> str:
        return (
            f"VoiceList(entity_type={self.entity_type!r}, "
            f"voices={len(self._voices)}, entities={len(self.entities)})"
        )