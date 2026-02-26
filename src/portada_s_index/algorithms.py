"""
Algoritmos de similitud de cadenas para desambiguación de términos.
"""

import math
from typing import Set, Tuple, List


# =============================================================================
# GRUPOS DE CONFUSIÓN OCR
# =============================================================================

OCR_CONFUSION_GROUPS = [
    {"c", "e"},
    {"p", "n", "r"},
    {"a", "o"},
    {"l", "i", "1"},
    {"m", "n"},
    {"u", "v"},
    {"g", "q"},
    {"h", "b"},
    {"d", "cl"},
    {"rn", "m"},
    {"f", "t"},
    {"s", "5"},
]

# Precalcular pares de confusión
_OCR_CONFUSION_PAIRS: Set[Tuple[str, str]] = set()
for group in OCR_CONFUSION_GROUPS:
    items = list(group)
    for i, x in enumerate(items):
        for y in items[i + 1 :]:
            _OCR_CONFUSION_PAIRS.add((x, y))
            _OCR_CONFUSION_PAIRS.add((y, x))


def ocr_substitution_cost(ca: str, cb: str, confusion_cost: float = 0.4) -> float:
    """
    Calcula el costo de sustitución considerando confusiones OCR.
    
    Args:
        ca: Primer carácter
        cb: Segundo carácter
        confusion_cost: Costo para sustituciones OCR comunes (default: 0.4)
    
    Returns:
        Costo de sustitución (0.0 si son iguales, confusion_cost si son confusión OCR, 1.0 en otro caso)
    """
    if ca == cb:
        return 0.0
    if (ca, cb) in _OCR_CONFUSION_PAIRS:
        return confusion_cost
    return 1.0


# =============================================================================
# DISTANCIA DE LEVENSHTEIN
# =============================================================================

def levenshtein_distance(a: str, b: str) -> int:
    """
    Calcula la distancia de Levenshtein estándar entre dos cadenas.
    
    Args:
        a: Primera cadena
        b: Segunda cadena
    
    Returns:
        Número mínimo de operaciones (inserción, eliminación, sustitución) para transformar a en b
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            insertions = current[j - 1] + 1
            deletions = previous[j] + 1
            substitutions = previous[j - 1] + (ca != cb)
            current.append(min(insertions, deletions, substitutions))
        previous = current
    
    return previous[-1]


def levenshtein_ratio(a: str, b: str) -> float:
    """
    Calcula la similitud de Levenshtein normalizada (0.0 a 1.0).
    
    Args:
        a: Primera cadena
        b: Segunda cadena
    
    Returns:
        Ratio de similitud (1.0 = idénticas, 0.0 = completamente diferentes)
    """
    max_len = max(len(a), len(b), 1)
    distance = levenshtein_distance(a, b)
    return 1.0 - distance / max_len


def levenshtein_distance_ocr(a: str, b: str, confusion_cost: float = 0.4) -> float:
    """
    Calcula la distancia de Levenshtein con costos ajustados para errores OCR.
    
    Args:
        a: Primera cadena
        b: Segunda cadena
        confusion_cost: Costo para sustituciones OCR comunes (default: 0.4)
    
    Returns:
        Distancia de Levenshtein con costos OCR
    """
    if a == b:
        return 0.0
    if not a:
        return float(len(b))
    if not b:
        return float(len(a))
    
    previous = [float(i) for i in range(len(b) + 1)]
    for i, ca in enumerate(a, start=1):
        current = [float(i)]
        for j, cb in enumerate(b, start=1):
            insertions = current[j - 1] + 1.0
            deletions = previous[j] + 1.0
            substitutions = previous[j - 1] + ocr_substitution_cost(ca, cb, confusion_cost)
            current.append(min(insertions, deletions, substitutions))
        previous = current
    
    return previous[-1]


def levenshtein_ratio_ocr(a: str, b: str, confusion_cost: float = 0.4) -> float:
    """
    Calcula la similitud de Levenshtein OCR normalizada.
    Para cadenas cortas (<=5 caracteres) usa OCR, para largas usa Levenshtein estándar.
    
    Args:
        a: Primera cadena
        b: Segunda cadena
        confusion_cost: Costo para sustituciones OCR comunes (default: 0.4)
    
    Returns:
        Ratio de similitud con corrección OCR
    """
    if len(a) <= 5 and len(b) <= 5:
        max_len = max(len(a), len(b), 1)
        distance = levenshtein_distance_ocr(a, b, confusion_cost)
        return 1.0 - distance / max_len
    return levenshtein_ratio(a, b)


# =============================================================================
# JARO-WINKLER
# =============================================================================

def jaro_winkler_similarity(a: str, b: str, prefix_weight: float = 0.1) -> float:
    """
    Calcula la similitud de Jaro-Winkler entre dos cadenas.
    Da mayor peso a las coincidencias en los prefijos.
    
    Args:
        a: Primera cadena
        b: Segunda cadena
        prefix_weight: Peso del prefijo común (default: 0.1)
    
    Returns:
        Similitud Jaro-Winkler (0.0 a 1.0)
    """
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    
    # Calcular distancia máxima para matches
    max_distance = max(len(a), len(b)) // 2 - 1
    if max_distance < 0:
        max_distance = 0
    
    # Encontrar matches
    matches_a = [False] * len(a)
    matches_b = [False] * len(b)
    matches = 0
    
    for i, char_a in enumerate(a):
        start = max(0, i - max_distance)
        end = min(i + max_distance + 1, len(b))
        for j in range(start, end):
            if matches_b[j] or char_a != b[j]:
                continue
            matches_a[i] = True
            matches_b[j] = True
            matches += 1
            break
    
    if matches == 0:
        return 0.0
    
    # Calcular transposiciones
    transpositions = 0
    k = 0
    for i, matched in enumerate(matches_a):
        if not matched:
            continue
        while not matches_b[k]:
            k += 1
        if a[i] != b[k]:
            transpositions += 1
        k += 1
    transpositions //= 2
    
    # Calcular similitud Jaro
    jaro = (
        (matches / len(a)) + 
        (matches / len(b)) + 
        ((matches - transpositions) / matches)
    ) / 3
    
    # Calcular longitud del prefijo común (máximo 4)
    prefix_len = 0
    for ca, cb in zip(a, b):
        if ca != cb or prefix_len == 4:
            break
        prefix_len += 1
    
    # Aplicar bonus de Winkler
    return jaro + prefix_len * prefix_weight * (1 - jaro)


# =============================================================================
# N-GRAMAS
# =============================================================================

def ngram_similarity(a: str, b: str, n: int = 2) -> float:
    """
    Calcula la similitud basada en n-gramas (Jaccard).
    
    Args:
        a: Primera cadena
        b: Segunda cadena
        n: Tamaño del n-grama (default: 2)
    
    Returns:
        Similitud basada en n-gramas (0.0 a 1.0)
    """
    def get_ngrams(text: str, n: int) -> Set[str]:
        """Extrae n-gramas de un texto."""
        if len(text) < n:
            return {text} if text else set()
        return {text[i:i + n] for i in range(len(text) - n + 1)}
    
    ngrams_a = get_ngrams(a, n)
    ngrams_b = get_ngrams(b, n)
    
    if not ngrams_a and not ngrams_b:
        return 1.0
    if not ngrams_a or not ngrams_b:
        return 0.0
    
    intersection = len(ngrams_a & ngrams_b)
    union = len(ngrams_a | ngrams_b)
    
    return intersection / union if union > 0 else 0.0


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Calcula la similitud de coseno entre dos vectores.
    
    Args:
        v1: Primer vector
        v2: Segundo vector
    
    Returns:
        Similitud de coseno (0.0 a 1.0)
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_v1 = math.sqrt(sum(x * x for x in v1))
    norm_v2 = math.sqrt(sum(x * x for x in v2))
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    
    return dot_product / (norm_v1 * norm_v2)
