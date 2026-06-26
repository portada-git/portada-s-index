import importlib.util
import sys
import types
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src" / "portada_s_index"

package = types.ModuleType("portada_s_index")
package.__path__ = [str(SRC_DIR)]
sys.modules.setdefault("portada_s_index", package)

algorithms_package = types.ModuleType("portada_s_index.algorithms")
algorithms_package.__path__ = [str(SRC_DIR / "algorithms")]
sys.modules.setdefault("portada_s_index.algorithms", algorithms_package)


def load_module(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, SRC_DIR / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


base_module = load_module("portada_s_index.algorithms.base", "algorithms/base.py")


class LengthSimilarity(base_module.Algorithm):
    name = "length_similarity"

    def similarity(self, a: str, b: str) -> float:
        return 1.0 - abs(len(a) - len(b)) / max(len(a), len(b), 1)


class BestMatchesMemorySafeTests(unittest.TestCase):
    def test_best_matches_keeps_only_one_voice_per_term(self):
        algorithm = LengthSimilarity({})
        preprocessed = algorithm.preprocess(
            terms=["aa", "aaaa"],
            voices=["a", "aa", "aaaa", "aaaaaa"],
        )

        best = algorithm.best_matches(preprocessed)

        self.assertEqual(best, {"aa": ("aa", 1.0), "aaaa": ("aaaa", 1.0)})


if __name__ == "__main__":
    unittest.main()
