"""
Funciones puras de normalización de texto.

Sin dependencias externas. Importable de forma aislada.
Todas las funciones son deterministas y sin estado.
"""

import re
import unicodedata
from functools import lru_cache


# Artículos y tratamientos que se eliminan en normalización semántica
_ARTICULOS = re.compile(
    r"\b(de\s+la|de\s+los|del|de|la|le|les|du|des|von|van|hms|el|los|las)\b",
    re.IGNORECASE,
)
_SANTOS = re.compile(
    r"\b(san|santa|saint|sainte|st)\b",
    re.IGNORECASE,
)
_TRATAMIENTOS = re.compile(
    r"\b(cpt|capt|cap|cptn|capitan|capitaine|captain|cmdr|comdr|"
    r"don|dn|sr|mr|msr|sieur|senor|monsieur|m)\b\.?\s*",
    re.IGNORECASE,
)


@lru_cache(maxsize=50_000)
def normalize(text: str) -> str:
    """
    Normalización canónica básica.

    Pasos: descompone Unicode → elimina diacríticos → minúsculas
    → elimina caracteres no alfanuméricos (conserva espacios y guiones)
    → colapsa espacios múltiples.

    Ejemplo:
        "Bergantín-Barca" → "bergantin-barca"
        "Capitán  J."     → "capitan  j"
    """
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    lowered = without_marks.lower()
    cleaned = re.sub(r"[^a-z0-9\s\-]", " ", lowered)
    return " ".join(cleaned.split())


@lru_cache(maxsize=50_000)
def normalize_semantic(text: str) -> str:
    """
    Normalización más agresiva para comparación semántica.

    Elimina artículos, tratamientos, abreviaturas de una letra
    y santos antes de comparar. Útil para embeddings y Jaccard.

    Ejemplo:
        "Cap. de la Mar"  → "mar"
        "San Juan"        → "san juan"  (san se normaliza a "san")
    """
    s = _strip_diacritics(text).lower()
    s = _TRATAMIENTOS.sub(" ", s)
    s = _ARTICULOS.sub(" ", s)
    s = _SANTOS.sub("san", s)
    s = re.sub(r"\b[a-z]\.\s*", " ", s)   # abreviaturas de 1 letra
    s = re.sub(r"[^a-z\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    tokens = [t for t in s.split() if len(t) >= 2]
    return " ".join(tokens) if tokens else text.lower().strip()


def tokenize_semantic(text: str) -> list[str]:
    """
    Devuelve la lista de tokens resultante de normalize_semantic.
    Útil para Jaccard de tokens.
    """
    return normalize_semantic(text).split()


def _strip_diacritics(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )