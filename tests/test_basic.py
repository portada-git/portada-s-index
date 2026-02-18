"""
Tests básicos para portada-s-index.
"""

import json
from portada_s_index import (
    SimilarityAlgorithm,
    SimilarityConfig,
    ClassificationLevel,
    calculate_similarity,
    classify_terms,
    normalize_text,
    levenshtein_distance,
    levenshtein_ratio,
    jaro_winkler_similarity,
    ngram_similarity,
)


def test_normalize_text():
    """Test de normalización de texto."""
    assert normalize_text("Alemán") == "aleman"
    assert normalize_text("FRANÇA") == "franca"
    assert normalize_text("España") == "espana"
    assert normalize_text("  múltiple   espacios  ") == "multiple espacios"
    print("✓ test_normalize_text passed")


def test_levenshtein_distance():
    """Test de distancia de Levenshtein."""
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("aleman", "aleman") == 0
    assert levenshtein_distance("", "abc") == 3
    print("✓ test_levenshtein_distance passed")


def test_levenshtein_ratio():
    """Test de ratio de Levenshtein."""
    assert levenshtein_ratio("aleman", "aleman") == 1.0
    assert 0.0 <= levenshtein_ratio("aleman", "frances") <= 1.0
    print("✓ test_levenshtein_ratio passed")


def test_jaro_winkler():
    """Test de Jaro-Winkler."""
    assert jaro_winkler_similarity("aleman", "aleman") == 1.0
    assert jaro_winkler_similarity("", "") == 1.0
    assert jaro_winkler_similarity("abc", "") == 0.0
    print("✓ test_jaro_winkler passed")


def test_ngram_similarity():
    """Test de similitud de n-gramas."""
    assert ngram_similarity("aleman", "aleman", n=2) == 1.0
    assert 0.0 <= ngram_similarity("aleman", "frances", n=2) <= 1.0
    print("✓ test_ngram_similarity passed")


def test_calculate_similarity():
    """Test de cálculo de similitud."""
    term = "aleman"
    voices = ["aleman", "alemana", "frances"]
    
    results = calculate_similarity(term, voices)
    
    assert len(results) > 0
    assert all(isinstance(algo, SimilarityAlgorithm) for algo in results.keys())
    assert all(0.0 <= result.similarity <= 1.0 for result in results.values())
    
    # Verificar que encuentra la mejor coincidencia
    for result in results.values():
        if result.voice == "aleman":
            assert result.similarity == 1.0
    
    print("✓ test_calculate_similarity passed")


def test_classify_terms():
    """Test de clasificación de términos."""
    terms = ["aleman", "frances", "desconocido"]
    voices = ["aleman", "alemana", "frances", "francesa"]
    frequencies = {"aleman": 100, "frances": 80, "desconocido": 5}
    
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        frequencies=frequencies,
    )
    
    assert len(classifications) == len(terms)
    
    for classification in classifications:
        assert classification.term in terms
        assert classification.frequency == frequencies[classification.term]
        assert isinstance(classification.classification, ClassificationLevel)
        assert classification.votes_approval >= 0
    
    print("✓ test_classify_terms passed")


def test_similarity_config():
    """Test de configuración de similitud."""
    config = SimilarityConfig(
        algorithms=[
            SimilarityAlgorithm.LEVENSHTEIN_OCR,
            SimilarityAlgorithm.JARO_WINKLER,
        ],
        thresholds={
            SimilarityAlgorithm.LEVENSHTEIN_OCR: 0.80,
            SimilarityAlgorithm.JARO_WINKLER: 0.85,
        },
    )
    
    # Test to_dict
    config_dict = config.to_dict()
    assert "algorithms" in config_dict
    assert "thresholds" in config_dict
    assert len(config_dict["algorithms"]) == 2
    
    # Test to_json
    config_json = config.to_json()
    assert isinstance(config_json, str)
    
    # Test from_dict
    config2 = SimilarityConfig.from_dict(config_dict)
    assert len(config2.algorithms) == len(config.algorithms)
    
    # Test from_json
    config3 = SimilarityConfig.from_json(config_json)
    assert len(config3.algorithms) == len(config.algorithms)
    
    print("✓ test_similarity_config passed")


def test_json_serialization():
    """Test de serialización JSON."""
    terms = ["aleman"]
    voices = ["aleman", "alemana"]
    
    classifications = classify_terms(terms, voices)
    
    # Test to_dict
    for classification in classifications:
        data = classification.to_dict()
        assert isinstance(data, dict)
        assert "term" in data
        assert "classification" in data
        assert "results" in data
    
    # Test to_json
    for classification in classifications:
        json_str = classification.to_json()
        assert isinstance(json_str, str)
        # Verificar que es JSON válido
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
    
    print("✓ test_json_serialization passed")


def test_voice_to_entity_mapping():
    """Test de mapeo de voces a entidades."""
    terms = ["aleman", "frances"]
    voices = ["aleman", "alemana", "frances", "francesa"]
    
    voice_to_entity = {
        "aleman": "ALEMANIA",
        "alemana": "ALEMANIA",
        "frances": "FRANCIA",
        "francesa": "FRANCIA",
    }
    
    classifications = classify_terms(
        terms=terms,
        voices=voices,
        voice_to_entity=voice_to_entity,
    )
    
    for classification in classifications:
        if classification.entity_consensus:
            assert classification.entity_consensus in voice_to_entity.values()
    
    print("✓ test_voice_to_entity_mapping passed")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("Ejecutando tests...")
    print("=" * 70)
    
    test_normalize_text()
    test_levenshtein_distance()
    test_levenshtein_ratio()
    test_jaro_winkler()
    test_ngram_similarity()
    test_calculate_similarity()
    test_classify_terms()
    test_similarity_config()
    test_json_serialization()
    test_voice_to_entity_mapping()
    
    print("=" * 70)
    print("✓ Todos los tests pasaron correctamente")


if __name__ == "__main__":
    run_all_tests()
