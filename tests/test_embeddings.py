import unittest
from portada_s_index.embeddings import CharHashingEmbedding

class TestEmbeddings(unittest.TestCase):
    def test_char_hashing_embedding_basic(self):
        embedder = CharHashingEmbedding(dimensions=64, n_gram=3)
        vec = embedder.get_vector("aleman")
        
        self.assertEqual(len(vec), 64)
        # Vector should be normalized, so its magnitude should be close to 1
        magnitude = sum(x*x for x in vec) ** 0.5
        self.assertAlmostEqual(magnitude, 1.0)

    def test_char_hashing_embedding_empty(self):
        embedder = CharHashingEmbedding(dimensions=64)
        vec = embedder.get_vector("")
        self.assertEqual(vec, [0.0] * 64)

    def test_char_hashing_embedding_deterministic(self):
        embedder = CharHashingEmbedding()
        vec1 = embedder.get_vector("test")
        vec2 = embedder.get_vector("test")
        self.assertEqual(vec1, vec2)

    def test_char_hashing_embedding_different(self):
        embedder = CharHashingEmbedding()
        vec1 = embedder.get_vector("aleman")
        vec2 = embedder.get_vector("frances")
        self.assertNotEqual(vec1, vec2)

    def test_short_text(self):
        # Test text shorter than n_gram
        embedder = CharHashingEmbedding(n_gram=5)
        vec = embedder.get_vector("abc")
        self.assertEqual(len(vec), 128)
        magnitude = sum(x*x for x in vec) ** 0.5
        self.assertAlmostEqual(magnitude, 1.0)

if __name__ == "__main__":
    unittest.main()
