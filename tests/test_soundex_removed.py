import unittest
from pathlib import Path


class SoundexRemovalTests(unittest.TestCase):
    def test_soundex_is_not_registered(self):
        registry_source = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "portada_s_index"
            / "algorithms"
            / "__init__.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn('"soundex"', registry_source)
        self.assertNotIn("Soundex", registry_source)


if __name__ == "__main__":
    unittest.main()
