
import json
from portada_s_index.strategy import AlgorithmBuilder, Text2VecStrategy
from portada_s_index.embeddings import CharHashingEmbedding

def test_text2vec_real_embedding():
    strategy = AlgorithmBuilder.build("text2vec")
    
    d1 = {"id": "1", "citation": "barcelona"}
    d2 = {"id": "2", "voice": "barzelona"}
    
    # Test prepare_data actually adds real vectors
    d1_prep = strategy.prepare_data(d1)
    d2_prep = strategy.prepare_data(d2)
    
    assert "text2vec_vector" in d1_prep
    assert "text2vec_vector" in d2_prep
    assert len(d1_prep["text2vec_vector"]) == 128
    
    # Test calculate
    results = strategy.calculate(d1_prep, d2_prep)
    print(f"Similarity score (text2vec): {results[0][2]}")
    assert 0.0 <= results[0][2] <= 1.0

if __name__ == "__main__":
    try:
        test_text2vec_real_embedding()
        print("Test passed: Text2Vec with real Hashing Embeddings works.")
    except Exception as e:
        print(f"Test failed: {e}")
