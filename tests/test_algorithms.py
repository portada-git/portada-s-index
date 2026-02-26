import unittest
from portada_s_index.algorithms import (
    levenshtein_distance,
    levenshtein_ratio,
    levenshtein_distance_ocr,
    levenshtein_ratio_ocr,
    jaro_winkler_similarity,
    ngram_similarity,
    cosine_similarity,
    ocr_substitution_cost
)

class TestAlgorithms(unittest.TestCase):
    def test_ocr_substitution_cost(self):
        self.assertEqual(ocr_substitution_cost("a", "a"), 0.0)
        self.assertEqual(ocr_substitution_cost("a", "o"), 0.4)
        self.assertEqual(ocr_substitution_cost("c", "e"), 0.4)
        self.assertEqual(ocr_substitution_cost("a", "x"), 1.0)

    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(levenshtein_distance("", "abc"), 3)
        self.assertEqual(levenshtein_distance("abc", ""), 3)
        self.assertEqual(levenshtein_distance("abc", "abc"), 0)

    def test_levenshtein_ratio(self):
        self.assertEqual(levenshtein_ratio("abc", "abc"), 1.0)
        self.assertEqual(levenshtein_ratio("abc", "abd"), 1.0 - 1/3)
        self.assertEqual(levenshtein_ratio("", ""), 1.0)

    def test_levenshtein_distance_ocr(self):
        # "aleman" vs "alemon" (a/o confusion)
        self.assertAlmostEqual(levenshtein_distance_ocr("aleman", "alemon"), 0.4)
        # "aleman" vs "alexan" (m/x no confusion)
        self.assertAlmostEqual(levenshtein_distance_ocr("aleman", "alexan"), 1.0)

    def test_jaro_winkler(self):
        self.assertEqual(jaro_winkler_similarity("aleman", "aleman"), 1.0)
        self.assertEqual(jaro_winkler_similarity("", ""), 1.0)
        self.assertEqual(jaro_winkler_similarity("abc", ""), 0.0)
        # Check prefix bonus
        s1 = jaro_winkler_similarity("martha", "marhta")
        s2 = jaro_winkler_similarity("dwayne", "duane")
        self.assertTrue(s1 > 0.9)
        self.assertTrue(s2 < 0.9)

    def test_ngram_similarity(self):
        self.assertEqual(ngram_similarity("aleman", "aleman", n=2), 1.0)
        self.assertEqual(ngram_similarity("", "", n=2), 1.0)
        self.assertEqual(ngram_similarity("abc", "def", n=2), 0.0)
        # "abc", "abd" -> bigrams: {"ab", "bc"}, {"ab", "bd"}
        # Intersection: {"ab"} (1), Union: {"ab", "bc", "bd"} (3) -> 1/3
        self.assertAlmostEqual(ngram_similarity("abc", "abd", n=2), 1/3)

    def test_cosine_similarity(self):
        self.assertEqual(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)
        self.assertAlmostEqual(cosine_similarity([1.0, 1.0], [1.0, 0.0]), 0.7071067811865475)
        self.assertEqual(cosine_similarity([], []), 0.0)
        self.assertEqual(cosine_similarity([1.0], [1.0, 2.0]), 0.0)

if __name__ == "__main__":
    unittest.main()
