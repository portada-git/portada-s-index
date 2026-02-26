import unittest
from portada_s_index.strategy import (
    AlgorithmBuilder,
    LevenshteinRatioStrategy,
    LevenshteinOcrStrategy,
    JaroWinklerStrategy,
    NgramStrategy,
    Text2VecStrategy
)
from portada_s_index.similarity import SimilarityAlgorithm

class TestStrategy(unittest.TestCase):
    def test_levenshtein_strategy(self):
        strategy = LevenshteinRatioStrategy()
        d1 = strategy.prepare_data({"id": "1", "citation": "aleman"})
        d2 = strategy.prepare_data({"id": "2", "voice": "alemon"})
        res = strategy.calculate(d1, d2)
        score = res[0][2]
        self.assertAlmostEqual(score, 1.0 - 1/6)

    def test_ocr_strategy(self):
        # Use short strings because LevenshteinOcrStrategy falls back to standard Levenshtein for len > 5
        # And use characters in OCR_CONFUSION_GROUPS (e.g., 'a' and 'o')
        strategy = LevenshteinOcrStrategy(confusion_cost=0.5)
        d1 = strategy.prepare_data({"id": "1", "citation": "casa"})
        d2 = strategy.prepare_data({"id": "2", "voice": "cosa"})
        res = strategy.calculate(d1, d2)
        score = res[0][2]
        # a/o is confusion -> cost 0.5. Similarity = 1 - 0.5/4 = 0.875
        self.assertAlmostEqual(score, 0.875)

    def test_jaro_winkler_strategy(self):
        strategy = JaroWinklerStrategy()
        d1 = strategy.prepare_data({"id": "1", "citation": "aleman"})
        d2 = strategy.prepare_data({"id": "2", "voice": "aleman"})
        res = strategy.calculate(d1, d2)
        score = res[0][2]
        self.assertEqual(score, 1.0)

    def test_ngram_strategy(self):
        strategy = NgramStrategy(n=2)
        d1 = strategy.prepare_data({"id": "1", "citation": "abc"})
        d2 = strategy.prepare_data({"id": "2", "voice": "abc"})
        res = strategy.calculate(d1, d2)
        score = res[0][2]
        self.assertEqual(score, 1.0)

    def test_text2vec_strategy(self):
        strategy = Text2VecStrategy(dimensions=64)
        d1 = strategy.prepare_data({"id": "1", "citation": "aleman"})
        d2 = strategy.prepare_data({"id": "2", "voice": "aleman"})
        res = strategy.calculate(d1, d2)
        score = res[0][2]
        self.assertAlmostEqual(score, 1.0)
        
        d3 = strategy.prepare_data({"id": "3", "voice": "frances"})
        res_diff = strategy.calculate(d1, d3)
        score_diff = res_diff[0][2]
        self.assertTrue(score_diff < 1.0)

    def test_algorithm_builder(self):
        builder = AlgorithmBuilder()
        
        strategy = builder.build(SimilarityAlgorithm.LEVENSHTEIN_RATIO.value)
        self.assertIsInstance(strategy, LevenshteinRatioStrategy)
        
        strategy = builder.build(SimilarityAlgorithm.LEVENSHTEIN_OCR.value)
        self.assertIsInstance(strategy, LevenshteinOcrStrategy)
        
        strategy = builder.build(SimilarityAlgorithm.TEXT2VEC.value)
        self.assertIsInstance(strategy, Text2VecStrategy)

if __name__ == "__main__":
    unittest.main()
