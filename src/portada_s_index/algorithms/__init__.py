# ARCHIVO: src/portada_s_index/algorithms/__init__.py
"""
Registro de algoritmos disponibles.

Conecta el nombre del JSON de configuración con la clase Python correcta.
Añadir un algoritmo nuevo: implementar la clase y registrarla aquí.
El pipeline no necesita ser modificado.
"""

from __future__ import annotations

from typing import Any

from portada_s_index.algorithms.base import Algorithm, AlgorithmNotAvailableError
from portada_s_index.algorithms.lexical import (
    LevenshteinOCR,
    LevenshteinRatio,
    JaroWinkler,
    NGram2,
    NGram3,
    NGram4,
)
from portada_s_index.algorithms.phonetic import PhoneticDM, Soundex
from portada_s_index.algorithms.semantic import TokenJaccard, CharCosine, SemanticModel, FastTextModel, ByT5Model
from portada_s_index.config import AlgorithmConfig


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------
# Clave: nombre exacto en el JSON de configuración
# Valor: clase que implementa Algorithm

REGISTRY: dict[str, type[Algorithm]] = {
    "levenshtein_ocr":   LevenshteinOCR,
    "levenshtein_ratio": LevenshteinRatio,
    "jaro_winkler":      JaroWinkler,
    "ngram_2":           NGram2,
    "ngram_3":           NGram3,
    "ngram_4":           NGram4,
    "phonetic_dm":       PhoneticDM,
    "soundex":           Soundex,
    "semantica":         TokenJaccard,
    "text2vec":          CharCosine,
    "semantic_model":    SemanticModel,
    "fasttext":          FastTextModel,
    "byt5":              ByT5Model,
}


def build(config: AlgorithmConfig) -> Algorithm:
    """
    Instancia un algoritmo a partir de su configuración.

    Raises:
        KeyError: Si el nombre del algoritmo no está en el registro.
        AlgorithmNotAvailableError: Si la dependencia opcional no está instalada.
    """
    if config.name not in REGISTRY:
        available = ", ".join(sorted(REGISTRY.keys()))
        raise KeyError(
            f"Algoritmo '{config.name}' no reconocido.\n"
            f"Algoritmos disponibles: {available}"
        )
    cls = REGISTRY[config.name]
    return cls(params=config.params)


def available_names() -> list[str]:
    """Devuelve los nombres de todos los algoritmos registrados."""
    return sorted(REGISTRY.keys())