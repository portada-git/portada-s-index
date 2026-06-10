import importlib.util
import sys
import types
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src" / "portada_s_index"

package = types.ModuleType("portada_s_index")
package.__path__ = [str(SRC_DIR)]
sys.modules.setdefault("portada_s_index", package)

config_spec = importlib.util.spec_from_file_location(
    "portada_s_index.config", SRC_DIR / "config.py"
)
config_module = importlib.util.module_from_spec(config_spec)
sys.modules["portada_s_index.config"] = config_module
config_spec.loader.exec_module(config_module)

PipelineConfig = config_module.PipelineConfig
ConfigValidationError = config_module.ConfigValidationError


class AlgorithmPerEntityConfigTests(unittest.TestCase):
    def test_v2_activates_algorithms_from_entity_mapping_without_enabled_flags(self):
        config = PipelineConfig.from_dict(
            {
                "version": 2,
                "normalize": False,
                "consensus": {"min_votes": "dynamic", "require_algorithm": False},
                "algorithms": {
                    "levenshtein_ratio": {
                        "threshold": 0.75,
                        "gray_zone": [0.55, 0.75],
                        "params": {},
                    },
                    "jaro_winkler": {
                        "threshold": 0.9,
                        "gray_zone": [0.7, 0.9],
                        "params": {},
                    },
                    "ngram_3": {
                        "threshold": 0.75,
                        "gray_zone": [0.55, 0.75],
                        "params": {},
                    },
                },
                "algorithm_per_entity": {
                    "port": ["levenshtein_ratio", "jaro_winkler"],
                    "ship": ["ngram_3"],
                },
            }
        )

        self.assertEqual(config.active_names_for_entity("port"), ["levenshtein_ratio", "jaro_winkler"])
        self.assertEqual(config.active_names_for_entity("ship"), ["ngram_3"])
        self.assertEqual(config.to_dict()["algorithm_per_entity"]["port"], ["levenshtein_ratio", "jaro_winkler"])

    def test_entity_mapping_rejects_algorithms_missing_from_algorithms_section(self):
        with self.assertRaisesRegex(ConfigValidationError, "algorithm_per_entity.port.*soundex"):
            PipelineConfig.from_dict(
                {
                    "version": 2,
                    "normalize": False,
                    "consensus": {"min_votes": "dynamic"},
                    "algorithms": {
                        "levenshtein_ratio": {
                            "threshold": 0.75,
                            "gray_zone": [0.55, 0.75],
                            "params": {},
                        }
                    },
                    "algorithm_per_entity": {
                        "port": ["levenshtein_ratio", "soundex"],
                    },
                }
            )


if __name__ == "__main__":
    unittest.main()
