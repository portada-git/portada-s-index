import unittest
import json
import os
import tempfile
from portada_s_index.json_interface import (
    calculate_similarity_json,
    classify_name_json,
    process_batch_json
)

class TestJsonInterface(unittest.TestCase):
    def test_calculate_similarity_json(self):
        input_data = {
            "term": "aleman",
            "voices": ["aleman", "alemana", "frances"]
        }
        json_input = json.dumps(input_data)
        json_output = calculate_similarity_json(json_input)
        
        output_data = json.loads(json_output)
        self.assertEqual(output_data["term"], "aleman")
        self.assertIn("results", output_data)
        self.assertIn("levenshtein_ocr", output_data["results"])
        self.assertEqual(output_data["results"]["levenshtein_ocr"]["voice"], "aleman")
        self.assertEqual(output_data["results"]["levenshtein_ocr"]["similarity"], 1.0)

    def test_classify_name_json(self):
        input_data = {
            "names": ["aleman", "frances"],
            "voices": ["aleman", "alemana", "frances", "francesa"],
            "frequencies": {"aleman": 100, "frances": 50}
        }
        json_input = json.dumps(input_data)
        json_output = classify_name_json(json_input)
        
        output_data = json.loads(json_output)
        self.assertIn("classifications", output_data)
        self.assertEqual(len(output_data["classifications"]), 2)
        self.assertEqual(output_data["classifications"][0]["term"], "aleman")
        self.assertEqual(output_data["classifications"][0]["classification"], "CONSENSUADO")

    def test_process_batch_json(self):
        input_data = {
            "operations": [
                {
                    "type": "calculate_similarity",
                    "data": {
                        "term": "aleman",
                        "voices": ["aleman", "alemana"]
                    }
                },
                {
                    "type": "classify_name",
                    "data": {
                        "names": ["frances"],
                        "voices": ["frances", "francesa"]
                    }
                }
            ]
        }
        json_input = json.dumps(input_data)
        json_output = process_batch_json(json_input)
        
        output_data = json.loads(json_output)
        self.assertEqual(output_data["total_operations"], 2)
        self.assertEqual(output_data["results"][0]["status"], "success")
        self.assertEqual(output_data["results"][1]["status"], "success")

if __name__ == "__main__":
    unittest.main()
