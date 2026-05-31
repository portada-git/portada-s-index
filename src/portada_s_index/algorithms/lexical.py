"""
Algoritmos léxicos de similitud de strings.

Implementaciones:
- LevenshteinRatio: Levenshtein estándar normalizado
- JaroWinkler     : Jaro-Winkler con peso de prefijo configurable
- NGram           : Similitud Jaccard de n-gramas de caracteres (n configurable)

Todas las funciones operan sobre strings ya normalizados.
Sin dependencias externas.
"""

from __future__ import annotations

from typing import Any, ClassVar

from portada_s_index.algorithms.base import Algorithm
from portada_s_index.normalize import normalize


# ---------------------------------------------------------------------------
# Funciones de distancia puras (sin estado, reutilizables)
# ---------------------------------------------------------------------------

def _levenshtein(a: str, b: str) -> int:
    """Distancia de Levenshtein clásica entre dos strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(
                curr[j - 1] + 1,
                prev[j] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = curr
    return prev[-1]


# ---------------------------------------------------------------------------
# Algoritmo 1: Levenshtein Ratio
# ---------------------------------------------------------------------------

class LevenshteinRatio(Algorithm):
    """
    Levenshtein estándar normalizado a [0, 1].

    similarity = 1 - distance / max(len(a), len(b))

    Params: ninguno.
    """

    name: ClassVar[str] = "levenshtein_ratio"

    def similarity(self, a: str, b: str) -> float:
        na, nb = normalize(a), normalize(b)
        max_len = max(len(na), len(nb), 1)
        return 1.0 - _levenshtein(na, nb) / max_len


# ---------------------------------------------------------------------------
# Algoritmo 2: Jaro-Winkler
# ---------------------------------------------------------------------------

class JaroWinkler(Algorithm):
    """
    Similitud Jaro-Winkler.

    Penaliza menos las diferencias en el prefijo común, lo que la hace
    especialmente adecuada para nombres propios y abreviaturas.

    Params:
        prefix_weight (float): Peso del prefijo compartido. Default 0.1.
                               El estándar es 0.1; valores > 0.25 no están definidos.
    """

    name: ClassVar[str] = "jaro_winkler"

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        self._prefix_weight = float(params.get("prefix_weight", 0.1))

    def similarity(self, a: str, b: str) -> float:
        na, nb = normalize(a), normalize(b)
        if na == nb:
            return 1.0
        if not na or not nb:
            return 0.0

        max_dist = max(len(na), len(nb)) // 2 - 1
        if max_dist < 0:
            max_dist = 0

        matches_a = [False] * len(na)
        matches_b = [False] * len(nb)
        matches = 0

        for i, ca in enumerate(na):
            start = max(0, i - max_dist)
            end = min(i + max_dist + 1, len(nb))
            for j in range(start, end):
                if matches_b[j] or ca != nb[j]:
                    continue
                matches_a[i] = True
                matches_b[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        transpositions = 0
        k = 0
        for i, matched in enumerate(matches_a):
            if not matched:
                continue
            while not matches_b[k]:
                k += 1
            if na[i] != nb[k]:
                transpositions += 1
            k += 1
        transpositions //= 2

        jaro = (
            (matches / len(na))
            + (matches / len(nb))
            + ((matches - transpositions) / matches)
        ) / 3.0

        prefix_len = 0
        for ca, cb in zip(na, nb):
            if ca != cb or prefix_len == 4:
                break
            prefix_len += 1

        return jaro + prefix_len * self._prefix_weight * (1.0 - jaro)


# ---------------------------------------------------------------------------
# Algoritmo 3/4/5: NGram (n configurable)
# ---------------------------------------------------------------------------

class NGram(Algorithm):
    """
    Similitud Jaccard de n-gramas de caracteres.

    Jaccard = |A ∩ B| / |A ∪ B|

    Robusta ante transposiciones y errores de OCR que no afectan
    todos los n-gramas a la vez.

    Params:
        n (int): Tamaño del n-grama. Default 2.
                 n=2 → bigramas, n=3 → trigramas, n=4 → cuatrigramas.
    """

    name: ClassVar[str] = "ngram"  # Sobreescrito por subclases

    def __init__(self, params: dict[str, Any]) -> None:
        super().__init__(params)
        self._n = int(params.get("n", 2))
        # El name se ajusta al n para que coincida con el registro
        self.name = f"ngram_{self._n}"  # type: ignore[misc]

    def similarity(self, a: str, b: str) -> float:
        na = normalize(a).replace(" ", "")
        nb = normalize(b).replace(" ", "")

        ngrams_a = self._get_ngrams(na)
        ngrams_b = self._get_ngrams(nb)

        if not ngrams_a and not ngrams_b:
            return 1.0
        if not ngrams_a or not ngrams_b:
            return 0.0

        intersection = len(ngrams_a & ngrams_b)
        union = len(ngrams_a | ngrams_b)
        return intersection / union if union > 0 else 0.0

    def _get_ngrams(self, text: str) -> set[str]:
        n = self._n
        if len(text) < n:
            return {text} if text else set()
        return {text[i: i + n] for i in range(len(text) - n + 1)}


class NGram2(NGram):
    name: ClassVar[str] = "ngram_2"

    def __init__(self, params: dict[str, Any]) -> None:
        params = dict(params)
        params["n"] = 2
        super().__init__(params)


class NGram3(NGram):
    name: ClassVar[str] = "ngram_3"

    def __init__(self, params: dict[str, Any]) -> None:
        params = dict(params)
        params["n"] = 3
        super().__init__(params)


class NGram4(NGram):
    name: ClassVar[str] = "ngram_4"

    def __init__(self, params: dict[str, Any]) -> None:
        params = dict(params)
        params["n"] = 4
        super().__init__(params)
