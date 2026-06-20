import importlib.util
import sys
import types
import unittest
from pathlib import Path

import numpy as np


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
load_module("portada_s_index.cache", "cache.py")
semantic_module = load_module("portada_s_index.algorithms.semantic", "algorithms/semantic.py")


class _NoGrad:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


class _TorchStub:
    float32 = "float32"
    float16 = "float16"
    bfloat16 = "bfloat16"

    @staticmethod
    def no_grad():
        return _NoGrad()


class _InputTensor:
    def to(self, device):
        return self


class _TokenizerStub:
    def __call__(self, batch, return_tensors, padding, truncation, max_length):
        return {"input_ids": _InputTensor(), "attention_mask": _MaskTensor()}


class _MaskTensor(_InputTensor):
    def unsqueeze(self, dim):
        return self

    def expand(self, size):
        return self

    def float(self):
        return self

    def sum(self, dim):
        return self

    def clamp(self, min):
        return self


class _BFloat16LikeTensor:
    def __init__(self):
        self.cast_to_float32 = False

    def float(self):
        self.cast_to_float32 = True
        return self

    def size(self):
        return (1, 1, 2)

    def __mul__(self, other):
        return self

    def sum(self, dim):
        return self

    def __truediv__(self, other):
        return self

    def cpu(self):
        return self

    def numpy(self):
        if not self.cast_to_float32:
            raise TypeError("Got unsupported ScalarType BFloat16")
        return np.array([[1.0, 0.0]], dtype=np.float32)


class _EncoderStub:
    def __call__(self, **inputs):
        return types.SimpleNamespace(last_hidden_state=_BFloat16LikeTensor())


class _ModelStub:
    def __call__(self, **inputs):
        return _EncoderStub()(**inputs)


class ByT5BFloat16Tests(unittest.TestCase):
    def test_encode_casts_bfloat16_hidden_state_before_numpy(self):
        previous_torch = getattr(semantic_module, "_torch", None)
        semantic_module._torch = _TorchStub
        try:
            model = object.__new__(semantic_module.ByT5Model)
            model._device = "cpu"
            model._max_length = 128
            model._tokenizer = _TokenizerStub()
            model._model_nn = _ModelStub()

            vecs = model._encode(["bergantin"], batch_size=1)
        finally:
            if previous_torch is None:
                if hasattr(semantic_module, "_torch"):
                    delattr(semantic_module, "_torch")
            else:
                semantic_module._torch = previous_torch

        self.assertEqual(vecs.dtype, np.float32)
        self.assertEqual(vecs.shape, (1, 2))


if __name__ == "__main__":
    unittest.main()
