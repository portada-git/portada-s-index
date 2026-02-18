"""
Script de prueba rápida sin necesidad de instalación.
Ejecutar desde el directorio raíz del proyecto.
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
from portada_s_index import (
    SimilarityAlgorithm,
    SimilarityConfig,
    calculate_similarity,
    classify_terms,
    normalize_text,
)


def test_normalization():
    """Test de normalización."""
    print("=" * 70)
    print("TEST 1: Normalización de texto")
    print("=" * 70)
    
    tests = [
        ("Alemán", "aleman"),
        ("FRANÇA", "franca"),
        ("España", "espana"),
        ("  múltiple   espacios  ", "multiple espacios"),
    ]
    
    for original, expected in tests:
        result = normalize_text(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{original}' -> '{result}' (esperado: '{expected}')")
    
    print()


def test_simple_similarity():
    """Test de similitud simple."""
    print("=" * 70)
    print("TEST 2: Similitud simple")
    print("=" * 70)
    
    term = "alemán"
    voices = ["aleman", "alemana", "germano", "frances", "ingles"]
    
    print(f"\nTérmino: {term}")
    print(f"Voces: {voices}\n")
    
    results = calculate_similarity(term, voices)
    
    for algo, result in results.items():
        status = "✓" if result.approved else "○"
        print(f"{status} {algo.value:20} -> {result.voice:15} (sim: {result.similarity:.4f})")
    
    print()


def test_classification():
    """Test de clasificación."""
    print("=" * 70)
    print("TEST 3: Clasificación de términos")
    print("=" * 70)
    
    terms = ["aleman", "frances", "ingles", "italiano", "desconocido"]
    voices = ["aleman", "alemana", "frances", "francesa", "ingles", "inglesa", "italiano", "italiana"]
    frequencies = {
        "aleman": 100,
        "frances": 80,
        "ingles": 150,
        "italiano": 90,
        "desconocido": 5,
    }
    
    voice_to_entity = {
        "aleman": "ALEMANIA",
        "alemana": "ALEMANIA",
        "frances": "FRANCIA",
        "francesa": "FRANCIA",
        "ingles": "INGLATERRA",
        "inglesa": "INGLATERRA",
        "italiano": "ITALIA",
        "italiana": "ITALIA",
    }
    
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
        voice_to_entity=voice_to_entity,
    )
    
    print(f"\n{'Término':<15} {'Frecuencia':<12} {'Clasificación':<20} {'Entidad':<15} {'Votos'}")
    print("-" * 80)
    
    for c in classifications:
        print(f"{c.term:<15} {c.frequency:<12} {c.classification.value:<20} {c.entity_consensus:<15} {c.votes_approval}")
    
    print()


def test_json_output():
    """Test de salida JSON."""
    print("=" * 70)
    print("TEST 4: Salida JSON")
    print("=" * 70)
    
    terms = ["aleman", "frances"]
    voices = ["aleman", "alemana", "frances", "francesa"]
    frequencies = {"aleman": 100, "frances": 80}
    
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
    )
    
    # Convertir a JSON
    output = [c.to_dict() for c in classifications]
    json_str = json.dumps(output, indent=2, ensure_ascii=False)
    
    print("\nResultado JSON:")
    print(json_str)
    print()


def test_custom_config():
    """Test de configuración personalizada."""
    print("=" * 70)
    print("TEST 5: Configuración personalizada")
    print("=" * 70)
    
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
        min_votes_consensus=2,
    )
    
    print("\nConfiguración:")
    print(json.dumps(config.to_dict(), indent=2))
    
    term = "barcelona"
    voices = ["barcelona", "barzelona", "barcino", "madrid"]
    
    results = calculate_similarity(term, voices, config)
    
    print(f"\nTérmino: {term}")
    print(f"Voces: {voices}\n")
    
    for algo, result in results.items():
        status = "✓" if result.approved else "✗"
        print(f"{status} {algo.value:20} -> {result.voice:15} (sim: {result.similarity:.4f})")
    
    print()


def main():
    """Ejecuta todos los tests."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PORTADA S-INDEX - TESTS RÁPIDOS" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    try:
        test_normalization()
        test_simple_similarity()
        test_classification()
        test_json_output()
        test_custom_config()
        
        print("=" * 70)
        print("✓ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("=" * 70)
        print()
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
