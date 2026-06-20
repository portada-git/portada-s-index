import importlib.util
import sys
import tempfile
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
load_module("portada_s_index.cache", "cache.py")
semantic_module = load_module("portada_s_index.algorithms.semantic", "algorithms/semantic.py")


class FastTextAutoDownloadTests(unittest.TestCase):
    def setUp(self):
        self.previous_available = semantic_module._FASTTEXT_AVAILABLE
        self.previous_fasttext = getattr(semantic_module, "_fasttext", None)
        semantic_module._FASTTEXT_AVAILABLE = True

    def tearDown(self):
        semantic_module._FASTTEXT_AVAILABLE = self.previous_available
        if self.previous_fasttext is None:
            if hasattr(semantic_module, "_fasttext"):
                delattr(semantic_module, "_fasttext")
        else:
            semantic_module._fasttext = self.previous_fasttext
        sys.modules.pop("fasttext.util", None)

    def test_missing_model_still_fails_without_auto_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "cc.es.300.bin"
            with self.assertRaises(FileNotFoundError):
                semantic_module.FastTextModel({"model_path": str(missing)})

    def test_auto_download_uses_fasttext_util_when_model_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp) / "models"
            model_path = cache_dir / "cc.es.300.bin"
            calls = []

            util_module = types.ModuleType("fasttext.util")

            def fake_download_model(lang, if_exists="ignore"):
                calls.append((lang, if_exists, Path.cwd()))
                model_path.write_text("fake model")

            util_module.download_model = fake_download_model
            sys.modules["fasttext.util"] = util_module

            loaded = []
            semantic_module._fasttext = types.SimpleNamespace(
                load_model=lambda path: loaded.append(path) or object()
            )

            semantic_module.FastTextModel(
                {
                    "model_path": str(model_path),
                    "auto_download": True,
                    "lang": "es",
                    "cache_dir": str(cache_dir),
                }
            )

            self.assertEqual(calls, [("es", "ignore", cache_dir)])
            self.assertEqual(loaded, [str(model_path)])


if __name__ == "__main__":
    unittest.main()
