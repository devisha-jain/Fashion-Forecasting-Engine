"""
API Robustness and Security Unit Tests.
Tests Flask endpoints for valid input, error boundaries, input limits,
and credential leak prevention.
"""

import unittest
import json
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app


class TestFashionAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.sample_text = (
            "Runway collections at Lakme Fashion Week 2026 presented oversized handloom kurtas "
            "paired with relaxed bandhani cargo pants in butter yellow tones. Gen-Z youth are "
            "embracing this craftcore aesthetic across urban metros."
        )

    def test_get_home_status(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "active")
        self.assertIn("nlp_pipeline", data)

    def test_get_config_security_no_secrets_leaked(self):
        res = self.client.get("/api/config")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        raw_json_str = json.dumps(data)
        
        # Verify no sensitive keywords exist in output
        self.assertNotIn("GEMINI_API_KEY", raw_json_str)
        self.assertNotIn("UPSTASH_REDIS_TOKEN", raw_json_str)
        self.assertNotIn("password", raw_json_str.lower())
        self.assertIn("llm", data["config"])
        self.assertIn("nlp", data["config"])

    def test_analyze_valid_input(self):
        res = self.client.post("/api/analyze", json={
            "text": self.sample_text,
            "region": "Pan India",
            "year": "2026"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("nlp_analysis", data)
        self.assertIn("trends", data)
        self.assertIn("metadata", data)
        self.assertTrue(len(data["nlp_analysis"]["keywords"]) > 0)
        self.assertTrue(len(data["trends"]) > 0)

    def test_analyze_empty_input(self):
        res = self.client.post("/api/analyze", json={"text": ""})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_analyze_oversized_input(self):
        large_text = "fashion " * 2000  # > 14000 characters
        res = self.client.post("/api/analyze", json={"text": large_text})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("exceeds maximum allowed limit", data["error"])

    def test_analyze_malformed_payload(self):
        res = self.client.post("/api/analyze", data="invalid json string", content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_forecast_endpoint_valid(self):
        res = self.client.post("/api/forecast", json={
            "region": "Pan India",
            "year": "2026",
            "signals": ["bollywood", "college"]
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("forecasts", data)
        self.assertTrue(len(data["forecasts"]) >= 2)

    def test_forecast_endpoint_no_signals(self):
        res = self.client.post("/api/forecast", json={"signals": []})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
