import unittest
import importlib.util
import sys
import types
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

ConsensusConfig = config_module.ConsensusConfig
AlgorithmScore = scoring_module.AlgorithmScore
classify = scoring_module.classify


class ScoringClassificationTests(unittest.TestCase):
    def test_consensus_requires_majority_of_executed_algorithms(self):
        scores = [
            AlgorithmScore(
                algorithm="algo_1",
                best_voice="voice-a",
                best_entity="ENTITY_A",
                score=0.9,
                threshold=0.8,
                voted=True,
                in_gray_zone=False,
            ),
            AlgorithmScore(
                algorithm="algo_2",
                best_voice="voice-a",
                best_entity="ENTITY_A",
                score=0.88,
                threshold=0.8,
                voted=True,
                in_gray_zone=False,
            ),
            AlgorithmScore(
                algorithm="algo_3",
                best_voice="voice-b",
                best_entity="ENTITY_B",
                score=0.2,
                threshold=0.8,
                voted=False,
                in_gray_zone=False,
            ),
            AlgorithmScore(
                algorithm="algo_4",
                best_voice="voice-c",
                best_entity="ENTITY_C",
                score=0.2,
                threshold=0.8,
                voted=False,
                in_gray_zone=False,
            ),
            AlgorithmScore(
                algorithm="algo_5",
                best_voice="voice-d",
                best_entity="ENTITY_D",
                score=0.2,
                threshold=0.8,
                voted=False,
                in_gray_zone=False,
            ),
        ]

        result = classify(
            term="term",
            frequency=1,
            normalized="term",
            exact_match=False,
            consensus=ConsensusConfig(min_votes=2),
            scores=scores,
        )

        self.assertEqual(result.classification, "REJECTED")

        scores[2] = AlgorithmScore(
            algorithm="algo_3",
            best_voice="voice-a",
            best_entity="ENTITY_A",
            score=0.87,
            threshold=0.8,
            voted=True,
            in_gray_zone=False,
        )

        result = classify(
            term="term",
            frequency=1,
            normalized="term",
            exact_match=False,
            consensus=ConsensusConfig(min_votes=2),
            scores=scores,
        )

        self.assertEqual(result.classification, "CONSENSUS")

    def test_split_votes_without_consensus_are_rejected_not_some_vote(self):
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
                    best_voice="voice-b",
                    best_entity="ENTITY_B",
                    score=0.7,
                    threshold=0.55,
                    voted=True,
                    in_gray_zone=False,
                ),
            ],
        )

        self.assertEqual(result.classification, "REJECTED")


if __name__ == "__main__":
    unittest.main()
