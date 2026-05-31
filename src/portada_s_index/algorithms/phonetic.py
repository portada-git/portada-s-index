"""
Algoritmos fonéticos de similitud.

Implementaciones:
- PhoneticDM : Double Metaphone — codifica pronunciación en inglés/español

La dependencia `metaphone` es opcional.
Si no está instalada, se lanza AlgorithmNotAvailableError con instrucciones.
"""

from __future__ import annotations

from typing import Any, ClassVar

from portada_s_index.algorithms.base import Algorithm, AlgorithmNotAvailableError
from portada_s_index.normalize import normalize
from portada_s_index.algorithms.lexical import _levenshtein


# ---------------------------------------------------------------------------
# Imports opcionales
# ---------------------------------------------------------------------------

try:
    from metaphone import doublemetaphone as _doublemetaphone
    _DM_AVAILABLE = True
except ImportError:
    _DM_AVAILABLE = False

# ---------------------------------------------------------------------------
# Utilidades fonéticas
# ---------------------------------------------------------------------------

def _phonetic_codes_dm(text: str) -> list[str]:
    """
    Genera códigos Double Metaphone para un texto normalizado.
    Devuelve lista vacía si la dependencia no está disponible.
    """
    norm = normalize(text).replace(" ", "")
    if not norm:
        return []
    if _DM_AVAILABLE:
        codes = _doublemetaphone(norm)
        return [c for c in codes if c]
    return []


def _phonetic_sim_from_codes(codes_a: list[str], codes_b: list[str]) -> float:
    """
    Similitud 0-1 comparando dos listas de códigos fonéticos.

    Si hay coincidencia exacta entre cualquier par de códigos → 1.0.
    Si no, devuelve el mejor ratio Levenshtein entre los códigos.
    """
    if not codes_a or not codes_b:
        return 0.0
    if any(ca == cb for ca in codes_a for cb in codes_b if ca and cb):
        return 1.0
    best = 0.0
    for ca in codes_a:
        for cb in codes_b:
            if not ca or not cb:
                continue
            max_len = max(len(ca), len(cb), 1)
            ratio = 1.0 - _levenshtein(ca, cb) / max_len
            if ratio > best:
                best = ratio
    return best


# ---------------------------------------------------------------------------
# Algoritmo 7: Double Metaphone
# ---------------------------------------------------------------------------

class PhoneticDM(Algorithm):
    """
    Similitud fonética basada en Double Metaphone.

    Compara las representaciones fonéticas de los strings.
    Dos strings con pronunciación similar (ej: "bergantín" / "bercantín")
    tendrán score alto aunque difieran ortográficamente.

    Requiere: `pip install metaphone`.

    Params: ninguno.
    """

    name: ClassVar[str] = "phonetic_dm"

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        if not _DM_AVAILABLE:
            raise AlgorithmNotAvailableError(
                "phonetic_dm requiere 'metaphone'.\n"
                "Instala con: pip install metaphone"
            )

    def similarity(self, a: str, b: str) -> float:
        codes_a = _phonetic_codes_dm(a)
        codes_b = _phonetic_codes_dm(b)
        return _phonetic_sim_from_codes(codes_a, codes_b)
