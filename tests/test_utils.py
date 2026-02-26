import unittest
import os
import tempfile
import json
from pathlib import Path
from portada_s_index.utils import (
    load_voices_from_file,
    load_name_from_csv,
    export_classifications_to_json,
    generate_summary_report
)
from portada_s_index.similarity import TermClassification, ClassificationLevel, SimilarityResult, SimilarityAlgorithm

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_load_voices_from_file(self):
        voices_file = self.tmp_path / "voices.txt"
        content = """
ALEMANIA:
  - aleman
  - alemana

FRANCIA:
  - frances
  - francesa
"""
        voices_file.write_text(content, encoding="utf-8")
        
        voices, voice_to_entity = load_voices_from_file(voices_file)
        
        self.assertEqual(len(voices), 4)
        self.assertIn("aleman", voices)
        self.assertEqual(voice_to_entity["aleman"], "ALEMANIA")
        self.assertEqual(voice_to_entity["frances"], "FRANCIA")

    def test_load_name_from_csv(self):
        csv_file = self.tmp_path / "names.csv"
        content = """termino_normalizado,frecuencia,ejemplo_original
aleman,100,Alemán
frances,50,Francés
"""
        csv_file.write_text(content, encoding="utf-8")
        
        name, frequencies = load_name_from_csv(csv_file)
        
        self.assertEqual(len(name), 2)
        self.assertEqual(frequencies["aleman"], 100)
        self.assertEqual(frequencies["frances"], 50)

    def test_generate_summary_report(self):
        classifications = [
            TermClassification(
                term="aleman",
                frequency=100,
                results={},
                votes_approval=3,
                entity_consensus="ALEMANIA",
                voice_consensus="aleman",
                votes_entity=3,
                levenshtein_ocr_in_consensus=True,
                classification=ClassificationLevel.CONSENSUADO
            ),
            TermClassification(
                term="unknown",
                frequency=10,
                results={},
                votes_approval=0,
                entity_consensus="",
                voice_consensus="",
                votes_entity=0,
                levenshtein_ocr_in_consensus=False,
                classification=ClassificationLevel.RECHAZADO
            )
        ]
        
        report = generate_summary_report(classifications, total_occurrences=110)
        
        self.assertEqual(report["total_names"], 2)
        self.assertEqual(report["total_occurrences"], 110)
        self.assertEqual(report["by_level"]["CONSENSUADO"]["count"], 1)
        self.assertEqual(report["by_level"]["RECHAZADO"]["count"], 1)
        self.assertEqual(report["coverage"]["consensuado_strict"]["occurrences"], 100)

if __name__ == "__main__":
    unittest.main()
