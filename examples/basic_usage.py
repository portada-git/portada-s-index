"""
Ejemplo básico de uso de portada-s-index.
"""

import json
from portada_s_index import (
    SimilarityAlgorithm,
    SimilarityConfig,
    calculate_similarity,
    classify_terms,
)


def example_1_simple_similarity():
    """Ejemplo 1: Calcular similitud simple entre un término y voces."""
    print("=" * 70)
    print("EJEMPLO 1: Similitud simple")
    print("=" * 70)
    
    term = "alemán"
    voices = ["aleman", "alemana", "germano", "frances", "ingles"]
    
    # Usar configuración por defecto
    results = calculate_similarity(term, voices)
    
    print(f"\nTérmino: {term}")
    print(f"Voces: {voices}\n")
    
    for algo, result in results.items():
        print(f"{algo.value}:")
        print(f"  Mejor coincidencia: {result.voice}")
        print(f"  Similitud: {result.similarity:.4f}")
        print(f"  Aprobado: {result.approved}")
        print()


def example_2_custom_config():
    """Ejemplo 2: Usar configuración personalizada."""
    print("=" * 70)
    print("EJEMPLO 2: Configuración personalizada")
    print("=" * 70)
    
    # Crear configuración personalizada
    config = SimilarityConfig(
        algorithms=[
            SimilarityAlgorithm.LEVENSHTEIN_OCR,
            SimilarityAlgorithm.JARO_WINKLER,
        ],
        thresholds={
            SimilarityAlgorithm.LEVENSHTEIN_OCR: 0.80,
            SimilarityAlgorithm.JARO_WINKLER: 0.90,
        },
        normalize=True,
    )
    
    print("\nConfiguración:")
    print(json.dumps(config.to_dict(), indent=2))
    
    term = "barcelona"
    voices = ["barcelona", "barzelona", "barcino", "madrid", "valencia"]
    
    results = calculate_similarity(term, voices, config)
    
    print(f"\nTérmino: {term}")
    print(f"Voces: {voices}\n")
    
    for algo, result in results.items():
        print(f"{algo.value}:")
        print(f"  Mejor coincidencia: {result.voice}")
        print(f"  Similitud: {result.similarity:.4f}")
        print(f"  Aprobado: {result.approved}")
        print()


def example_3_classify_terms():
    """Ejemplo 3: Clasificar múltiples términos."""
    print("=" * 70)
    print("EJEMPLO 3: Clasificación de términos")
    print("=" * 70)
    
    terms = ["aleman", "frances", "ingles", "español", "italiano", "desconocido"]
    voices = ["aleman", "alemana", "frances", "francesa", "ingles", "inglesa", "español", "italiana"]
    frequencies = {
        "aleman": 100,
        "frances": 80,
        "ingles": 150,
        "español": 120,
        "italiano": 90,
        "desconocido": 5,
    }
    
    # Mapeo de voces a entidades
    voice_to_entity = {
        "aleman": "ALEMANIA",
        "alemana": "ALEMANIA",
        "frances": "FRANCIA",
        "francesa": "FRANCIA",
        "ingles": "INGLATERRA",
        "inglesa": "INGLATERRA",
        "español": "ESPAÑA",
        "italiana": "ITALIA",
    }
    
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
        voice_to_entity=voice_to_entity,
    )
    
    print("\nResultados de clasificación:\n")
    
    for classification in classifications:
        print(f"Término: {classification.term}")
        print(f"  Frecuencia: {classification.frequency}")
        print(f"  Clasificación: {classification.classification.value}")
        print(f"  Entidad consensuada: {classification.entity_consensus}")
        print(f"  Voz consensuada: {classification.voice_consensus}")
        print(f"  Votos: {classification.votes_approval}")
        print()


def example_4_json_output():
    """Ejemplo 4: Exportar resultados a JSON."""
    print("=" * 70)
    print("EJEMPLO 4: Exportación a JSON")
    print("=" * 70)
    
    terms = ["aleman", "frances"]
    voices = ["aleman", "alemana", "frances", "francesa"]
    
    classifications = classify_terms(terms, voices)
    
    # Convertir a JSON
    json_output = [c.to_dict() for c in classifications]
    
    print("\nResultados en JSON:")
    print(json.dumps(json_output, indent=2, ensure_ascii=False))


def example_5_all_algorithms():
    """Ejemplo 5: Comparar todos los algoritmos."""
    print("=" * 70)
    print("EJEMPLO 5: Comparación de todos los algoritmos")
    print("=" * 70)
    
    config = SimilarityConfig(
        algorithms=[
            SimilarityAlgorithm.LEVENSHTEIN_OCR,
            SimilarityAlgorithm.LEVENSHTEIN_RATIO,
            SimilarityAlgorithm.JARO_WINKLER,
            SimilarityAlgorithm.NGRAM_2,
            SimilarityAlgorithm.NGRAM_3,
        ]
    )
    
    term = "barcelona"
    voices = ["barcelona", "barzelona", "barcino"]
    
    results = calculate_similarity(term, voices, config)
    
    print(f"\nTérmino: {term}")
    print(f"Voces: {voices}\n")
    print(f"{'Algoritmo':<20} {'Mejor voz':<15} {'Similitud':<10} {'Aprobado'}")
    print("-" * 60)
    
    for algo, result in results.items():
        print(f"{algo.value:<20} {result.voice:<15} {result.similarity:<10.4f} {result.approved}")


if __name__ == "__main__":
    example_1_simple_similarity()
    print("\n")
    
    example_2_custom_config()
    print("\n")
    
    example_3_classify_terms()
    print("\n")
    
    example_4_json_output()
    print("\n")
    
    example_5_all_algorithms()
