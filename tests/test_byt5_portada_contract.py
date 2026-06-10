import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_SOURCE = ROOT / "portada-s-index" / "src" / "portada_s_index" / "algorithms" / "semantic.py"
BACKEND_CONFIG = ROOT / "portada_backend" / "config" / "config_similarity.json"
DATA_LAYER_CONFIG = ROOT / "data_layer_config" / "config_similarity.json"


class ByT5PortadaModelContractTests(unittest.TestCase):
    def test_implementation_uses_encoder_model_directly(self):
        source = SEMANTIC_SOURCE.read_text(encoding="utf-8")

        self.assertIn("T5EncoderModel", source)
        self.assertNotIn("AutoModel as _AutoModel", source)
        self.assertNotIn("self._model_nn.encoder(**inputs)", source)
        self.assertIn("self._model_nn(**inputs)", source)

    def test_implementation_uses_attention_masked_mean_pooling_with_model_max_length(self):
        source = SEMANTIC_SOURCE.read_text(encoding="utf-8")

        self.assertIn('max_length=self._max_length', source)
        self.assertIn('inputs["attention_mask"]', source)
        self.assertIn("mask.sum(1).clamp(min=1e-9)", source)
        self.assertNotIn("last_hidden_state.mean(dim=1)", source)

    def test_backend_configs_point_to_portada_contrastive_byt5_defaults(self):
        for path in [BACKEND_CONFIG, DATA_LAYER_CONFIG]:
            config = json.loads(path.read_text(encoding="utf-8"))
            params = config["algorithms"]["byt5"]["params"]
            self.assertEqual(params["model"], "agusnieto77/byt5-portada-contrastivo")
            self.assertEqual(params["torch_dtype"], "bfloat16")
            self.assertEqual(params["max_length"], 128)


if __name__ == "__main__":
    unittest.main()
