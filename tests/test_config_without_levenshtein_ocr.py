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

scoring_spec = importlib.util.spec_from_file_location(
    "portada_s_index.scoring", SRC_DIR / "scoring.py"
)
scoring_module = importlib.util.module_from_spec(scoring_spec)
sys.modules["portada_s_index.scoring"] = scoring_module
scoring_spec.loader.exec_module(scoring_module)

AlgorithmScore = scoring_module.AlgorithmScore
ConsensusConfig = config_module.ConsensusConfig
PipelineConfig = config_module.PipelineConfig
classify = scoring_module.classify


class LevenshteinOcrRemovalTests(unittest.TestCase):
    def test_pipeline_config_does_not_emit_levenshtein_ocr_consensus_flag(self):
        config = PipelineConfig.from_dict(
            {
                "version": 2,
                "normalize": True,
                "consensus": {
                    "min_votes": 2,
                    "require_levenshtein_ocr": True,
                },
                "algorithms": {},
            }
        )

        self.assertNotIn("require_levenshtein_ocr", config.to_dict()["consensus"])

    def test_consensus_does_not_require_levenshtein_ocr_vote(self):
        result = classify(
            term="term",
            frequency=1,
            normalized="term",
            exact_match=False,
            consensus=ConsensusConfig(min_votes=2),
            scores=[
                AlgorithmScore(
                    algorithm="jaro_winkler",
                    best_voice="voice-a",
                    best_entity="ENTITY_A",
                    score=0.9,
                    threshold=0.85,
                    voted=True,
                    in_gray_zone=False,
                ),
                AlgorithmScore(
                    algorithm="ngram_3",
                    best_voice="voice-a",
                    best_entity="ENTITY_A",
                    score=0.7,
                    threshold=0.55,
                    voted=True,
                    in_gray_zone=False,
                ),
            ],
        )

        self.assertEqual(result.classification, "CONSENSUS")


if __name__ == "__main__":
    unittest.main()
