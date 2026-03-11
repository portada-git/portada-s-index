"""
Resultado bruto de un algoritmo de similitud.

SimilarityMatrix contiene todos los pares (término, voz) con sus scores.
No aplica umbrales ni clasificación — eso es responsabilidad de scoring.py.

Corresponde a SimilarityMatrix y Similarity del diagrama de clases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(slots=True)
class Similarity:
    """
    Par (término, voz) con su score para un algoritmo.

    Corresponde a la clase Similarity del diagrama de clases:
        - citation_id      → término evaluado
        - voice_id         → voz candidata
        - algorithm_name   → nombre del algoritmo que produjo el score
        - similarity_value → score 0-1
    """
    citation_id: str        # Término normalizado
    voice_id: str           # Voz normalizada
    algorithm_name: str
    similarity_value: float


class SimilarityMatrix:
    """
    Colección de Similarity para un algoritmo concreto.

    Corresponde a SimilarityMatrix del diagrama de clases.
    Producido por Algorithm.process(); consumido por scoring.py.
    """

    def __init__(self, algorithm_name: str, entries: list[Similarity]) -> None:
        self.algorithm_name = algorithm_name
        self._entries = entries

        # Índice: term → lista de (voice, score)
        self._index: dict[str, list[tuple[str, float]]] = {}
        for e in entries:
            if e.citation_id not in self._index:
                self._index[e.citation_id] = []
            self._index[e.citation_id].append((e.voice_id, e.similarity_value))

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def best_for(self, term: str) -> Similarity | None:
        """La voz con mayor score para un término dado."""
        pairs = self._index.get(term)
        if not pairs:
            return None
        best_voice, best_score = max(pairs, key=lambda x: x[1])
        return Similarity(
            citation_id=term,
            voice_id=best_voice,
            algorithm_name=self.algorithm_name,
            similarity_value=best_score,
        )

    def scores_for(self, term: str) -> list[tuple[str, float]]:
        """Todos los pares (voz, score) para un término, ordenados desc."""
        pairs = self._index.get(term, [])
        return sorted(pairs, key=lambda x: x[1], reverse=True)

    def terms(self) -> list[str]:
        return list(self._index.keys())

    def __iter__(self) -> Iterator[Similarity]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)