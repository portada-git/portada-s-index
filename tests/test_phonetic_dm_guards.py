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


load_module("portada_s_index.algorithms.base", "algorithms/base.py")
load_module("portada_s_index.normalize", "normalize.py")
load_module("portada_s_index.algorithms.lexical", "algorithms/lexical.py")
phonetic_module = load_module("portada_s_index.algorithms.phonetic", "algorithms/phonetic.py")


class PhoneticDMGuardTests(unittest.TestCase):
    def setUp(self):
        self.previous_available = phonetic_module._DM_AVAILABLE
        self.previous_doublemetaphone = getattr(phonetic_module, "_doublemetaphone", None)
        phonetic_module._DM_AVAILABLE = True
        code_map = {
            "jacaro": ("JKR", "AKR"),
            "uchiura": ("AXR", "AKR"),
            "komedio": ("KMT", ""),
            "cameta": ("KMT", ""),
            "boo": ("P", ""),
            "pp": ("P", ""),
            "bergantin": ("PRKNTN", ""),
            "bercantin": ("PRKNTN", ""),
            "new-york": ("NRK", ""),
            "newark": ("NRK", ""),
        }
        phonetic_module._doublemetaphone = lambda text: code_map[text]

    def tearDown(self):
        phonetic_module._DM_AVAILABLE = self.previous_available
        if self.previous_doublemetaphone is None:
            delattr(phonetic_module, "_doublemetaphone")
        else:
            phonetic_module._doublemetaphone = self.previous_doublemetaphone

    def test_exact_phonetic_code_requires_textual_proximity(self):
        algorithm = phonetic_module.PhoneticDM({})

        self.assertLess(algorithm.similarity("komedio", "cameta"), 0.8)
        self.assertLess(algorithm.similarity("jacaro", "uchiura"), 0.8)
        self.assertLess(algorithm.similarity("boo", "pp"), 0.8)

    def test_close_ocr_variants_keep_strong_phonetic_match(self):
        algorithm = phonetic_module.PhoneticDM({})

        self.assertEqual(algorithm.similarity("bergantin", "bercantin"), 1.0)
        self.assertEqual(algorithm.similarity("new-york", "newark"), 1.0)


if __name__ == "__main__":
    unittest.main()
