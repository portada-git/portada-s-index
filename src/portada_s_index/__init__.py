"""
Portada S-Index: Biblioteca de algoritmos de similitud para desambiguación de términos históricos.

INTERFAZ PRINCIPAL: JSON
Todas las entradas y salidas se manejan mediante JSON.
"""

from .similarity import (
    SimilarityAlgorithm,
    SimilarityConfig,
    SimilarityResult,
    TermClassification,
    ClassificationLevel,
    calculate_similarity,
    classify_name,
    normalize_text,
)

from .core import (
    PortAdaSIndex,
    SimilarityMatrix,
    EntityCitation,
    KnownEntity,
)

from .algorithms import (
    levenshtein_distance,
    levenshtein_ratio,
    levenshtein_distance_ocr,
    levenshtein_ratio_ocr,
    jaro_winkler_similarity,
    ngram_similarity,
)

from .strategy import (
    SimilarityAlgorithmStrategy,
    LevenshteinRatioStrategy,
    LevenshteinOcrStrategy,
    JaroWinklerStrategy,
    NgramStrategy,
    AlgorithmBuilder,
)

from .utils import (
    load_voices_from_file,
    load_name_from_csv,
    export_classifications_to_json,
    export_classifications_by_level,
    generate_summary_report,
    export_summary_report,
)

from .json_interface import (
    calculate_similarity_json,
    classify_name_json,
    classify_name_with_report_json,
    calculate_similarity_from_file,
    classify_name_from_file,
    classify_name_with_report_from_file,
    process_batch_json,
    process_batch_from_file,
)

__version__ = "0.1.0"

__all__ = [
    # Enums y clases principales
    "PortAdaSIndex",
    "SimilarityMatrix",
    "EntityCitation",
    "KnownEntity",
    "SimilarityAlgorithm",
    "SimilarityConfig",
    "SimilarityResult",
    "TermClassification",
    "ClassificationLevel",
    # Strategy Pattern & Builders
    "SimilarityAlgorithmStrategy",
    "LevenshteinRatioStrategy",
    "LevenshteinOcrStrategy",
    "JaroWinklerStrategy",
    "NgramStrategy",
    "AlgorithmBuilder",
    # Funciones principales (uso interno)
    "calculate_similarity",
    "classify_name",
    "normalize_text",
    # Algoritmos individuales (uso interno)
    "levenshtein_distance",
    "levenshtein_ratio",
    "levenshtein_distance_ocr",
    "levenshtein_ratio_ocr",
    "jaro_winkler_similarity",
    "ngram_similarity",
    # Utilidades (uso interno)
    "load_voices_from_file",
    "load_name_from_csv",
    "export_classifications_to_json",
    "export_classifications_by_level",
    "generate_summary_report",
    "export_summary_report",
    # INTERFAZ JSON (uso principal)
    "calculate_similarity_json",
    "classify_name_json",
    "classify_name_with_report_json",
    "calculate_similarity_from_file",
    "classify_name_from_file",
    "classify_name_with_report_from_file",
    "process_batch_json",
    "process_batch_from_file",
]


def main() -> None:
    print("Portada S-Index - Biblioteca de similitud de términos")
    print(f"Versión: {__version__}")
    print("\nInterfaz principal: JSON")
    print("Usa las funciones *_json() o *_from_file() para entrada/salida JSON")
