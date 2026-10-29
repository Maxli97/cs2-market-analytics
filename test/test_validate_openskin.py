import unittest
import gzip
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from src.validate_openskin import Probe, positive_number, profile_fields, summarize_bulk


class ValidationTests(unittest.TestCase):
    def test_quote_validity(self):
        for value in (None, False, True, 0, -1, "12", float("nan"), float("inf")):
            self.assertFalse(positive_number(value))
        self.assertTrue(positive_number(0.01))

    def test_variants_and_coverage_preserve_names(self):
        data = {
            "StatTrak\u2122 AK-47 | Redline (Field-Tested)": {"steam": {"ask": 1, "bid": None}},
            "Souvenir AWP | Dragon Lore (Factory New)": {"steam": {"ask": None}, "csfloat": {"ask": 5, "highest_bid": 4}},
            "Sticker | Test": {"steam": None},
            "AK-47 | Redline (Field-Tested)": {"steam": {"ask": 0}},
        }
        result = summarize_bulk({"data": data, "count": 4})
        self.assertTrue(result["count_matches"])
        self.assertEqual(result["unique_names"], 4)
        self.assertEqual(result["variants"]["stattrak"], 1)
        self.assertEqual(result["variants"]["souvenir"], 1)
        self.assertEqual(result["variants"]["wear"]["Field-Tested"], 2)
        self.assertEqual(result["variants"]["no_wear_suffix"], 1)
        self.assertEqual(result["markets"]["steam"]["object_present"], 3)
        self.assertEqual(result["markets"]["steam"]["ask_coverage_pct"], 25)
        self.assertEqual(result["markets"]["csfloat"]["ask_and_bid"], 1)

    def test_null_missing_and_array_profile(self):
        fields = profile_fields([{"steam": {"ask": None}, "patterns": [{"paint_seed": 1}]}, {"steam": {"ask": 2}}])
        self.assertEqual(fields["steam.ask"], {"present": 2, "NoneType": 1, "int": 1})
        self.assertEqual(fields["patterns"]["present"], 1)
        self.assertNotIn("patterns.paint_seed", fields)

    def test_count_mismatch_and_empty_bulk(self):
        self.assertFalse(summarize_bulk({"data": {}, "count": 1})["count_matches"])
        self.assertEqual(summarize_bulk({"data": {}})["markets"]["steam"]["ask_coverage_pct"], 0)

    def test_compressed_response_size_and_error_status(self):
        with tempfile.TemporaryDirectory() as folder:
            probe = Probe(Path(folder), "https://example.test")
            decoded = b'{"error":"not found"}'
            wire = gzip.compress(decoded)

            def respond(command, **kwargs):
                Path(command[command.index("--output") + 1]).write_bytes(wire)
                Path(command[command.index("--dump-header") + 1]).write_text("Content-Encoding: gzip\n")
                return SimpleNamespace(returncode=0, stderr="", stdout=json.dumps({"http_code": 404, "size_download": len(wire)}))

            with patch("src.validate_openskin.subprocess.run", side_effect=respond), patch("src.validate_openskin.time.sleep"):
                self.assertIsNone(probe.request("unknown", "/v1/prices"))
            self.assertEqual(probe.requests[0]["decoded_bytes"], len(decoded))
            self.assertEqual(probe.requests[0]["saved_body_bytes"], len(wire))
            self.assertEqual(probe.requests[0]["http_status"], 404)

    def test_rate_limit_stops_requests(self):
        with tempfile.TemporaryDirectory() as folder:
            probe = Probe(Path(folder), "https://example.test")
            response = SimpleNamespace(returncode=0, stderr="", stdout='{"http_code":429}')
            with patch("src.validate_openskin.subprocess.run", return_value=response), patch("src.validate_openskin.time.sleep"):
                with self.assertRaises(RuntimeError):
                    probe.request("limited", "/health")
            self.assertEqual(probe.requests[0]["http_status"], 429)


if __name__ == "__main__":
    unittest.main()
