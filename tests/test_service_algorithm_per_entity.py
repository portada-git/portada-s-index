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
load_module("portada_s_index.normalize", "normalize.py")
load_module("portada_s_index.data.voice_list", "data/voice_list.py")
load_module("portada_s_index.data.citation", "data/citation.py")
load_module("portada_s_index.matrix", "matrix.py")
load_module("portada_s_index.scoring", "scoring.py")

algorithms_module = types.ModuleType("portada_s_index.algorithms")
algorithms_module.build = lambda config: None
sys.modules["portada_s_index.algorithms"] = algorithms_module
base_module = types.ModuleType("portada_s_index.algorithms.base")
base_module.Algorithm = object
base_module.PreprocessedData = object
sys.modules["portada_s_index.algorithms.base"] = base_module
cache_module = types.ModuleType("portada_s_index.cache")
cache_module.ModelCache = type(
    "ModelCache", (), {"get_model": staticmethod(lambda key, factory: factory())}
)
sys.modules["portada_s_index.cache"] = cache_module
load_module("portada_s_index.cleaning", "cleaning.py")
service_module = load_module("portada_s_index.service", "service.py")

PipelineConfig = config_module.PipelineConfig
SimilarityService = service_module.SimilarityService
VoiceList = sys.modules["portada_s_index.data.voice_list"].VoiceList
matrix_module = sys.modules["portada_s_index.matrix"]
SimilarityMatrix = matrix_module.SimilarityMatrix
Similarity = matrix_module.Similarity


class FakeAlgorithm:
    def __init__(self, name):
        self.name = name

    def set_config(self, params):
        pass

    def preprocess(self, terms, voices):
        return (terms, voices)

    def process(self, preprocessed):
        return SimilarityMatrix(
            self.name,
            [Similarity("sevilla", "sevilla", self.name, 1.0)],
        )


class ServiceAlgorithmPerEntityTests(unittest.TestCase):
    def test_evaluate_runs_all_configured_algorithms_and_exposes_entity_allowed_filter(self):
        calls = []

        def fake_build(config):
            calls.append(config.name)
            return FakeAlgorithm(config.name)

        original_build = service_module.build_algorithm
        service_module.build_algorithm = fake_build
        try:
            config = PipelineConfig.from_dict(
                {
                    "version": 2,
                    "normalize": True,
                    "consensus": {"min_votes": "dynamic"},
                    "algorithms": {
                        "levenshtein_ratio": {"threshold": 0.75, "gray_zone": [0.55, 0.75]},
                        "jaro_winkler": {"threshold": 0.9, "gray_zone": [0.7, 0.9]},
                        "ngram_3": {"threshold": 0.75, "gray_zone": [0.55, 0.75]},
                    },
                    "algorithm_per_entity": {
                        "port": ["levenshtein_ratio", "jaro_winkler"],
                        "ship": ["ngram_3"],
                    },
                }
            )
            service = SimilarityService(config)
            voice_list = VoiceList.from_dict("ship", {"SEVILLA": ["sevilla"]})

            results = service.evaluate(["sevilla"], voice_list)
        finally:
            service_module.build_algorithm = original_build

        self.assertEqual(calls, ["levenshtein_ratio", "jaro_winkler", "ngram_3"])
        self.assertEqual(results[0]["allowed_algorithms"], ["ngram_3"])
        self.assertEqual(
            [score["algorithm"] for score in results[0]["algorithm_scores"]],
            ["levenshtein_ratio", "jaro_winkler", "ngram_3"],
        )
        self.assertNotIn("classification", results[0])
        self.assertNotIn("entity", results[0])
        self.assertNotIn("votes", results[0])


if __name__ == "__main__":
    unittest.main()
