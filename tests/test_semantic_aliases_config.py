import importlib.util
import sys
import types
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src" / "portada_s_index"

package = types.ModuleType("portada_s_index")
package.__path__ = [str(SRC_DIR)]
sys.modules.setdefault("portada_s_index", package)


def load_module(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(module_name, SRC_DIR / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


config_module = load_module("portada_s_index.config", "config.py")


class SemanticAliasesConfigTests(unittest.TestCase):
    def test_threshold_pair_maps_to_threshold_and_gray_zone(self):
        config = config_module.PipelineConfig.from_dict(
            {
                "version": 2,
                "normalize": True,
                "consensus": {"min_votes": 2},
                "algorithms": {
                    "semantic_text2vec": {
                        "enabled": True,
                        "threshold": [0.95, 0.7],
                        "params": {"model": "shibing624/text2vec-base-multilingual"},
                    }
                },
            }
        )

        algorithm = config.algorithms["semantic_text2vec"]
        self.assertEqual(algorithm.threshold, 0.95)
        self.assertEqual(algorithm.gray_zone, (0.7, 0.95))

    def test_semantic_aliases_are_registered_to_semantic_model(self):
        registry_source = (
            SRC_DIR / "algorithms" / "__init__.py"
        ).read_text(encoding="utf-8")

        for name in [
            "semantic_text2vec",
            "sentence_transformer_LABSE",
            "sentence_transformer_labse",
            "sentence_transformer_mpnet",
        ]:
            self.assertIn(f'"{name}"', registry_source)


if __name__ == "__main__":
    unittest.main()
