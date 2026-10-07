"""
Unit Tests for LLM Prompt System, Schemas, and Fallback Resilience.
"""

import unittest
import json
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from llm.prompt_loader import PromptLoader
from llm.schemas import (
    ExtractedTrendItem,
    TrendExtractionResponse,
    TrendAnalysisResponse,
    YearlyForecastPoint,
    ForecastTrajectoryResponse
)
from llm.gemini_client import GeminiFashionClient


class TestLLMModule(unittest.TestCase):

    def setUp(self):
        self.prompt_loader = PromptLoader()
        self.client = GeminiFashionClient()

    def test_prompt_loader_templates_exist(self):
        templates = ["trend_extraction", "trend_analysis", "forecast_generation"]
        for t in templates:
            content = self.prompt_loader.get_template(t)
            self.assertTrue(len(content) > 50)
            self.assertIn("OUTPUT", content)

    def test_prompt_formatting(self):
        formatted = self.prompt_loader.format_prompt(
            "forecast_generation",
            trend_name="Bandhani Fusion",
            region="Gujarat",
            year="2026",
            year_minus_1="2025",
            year_plus_1="2027",
            year_plus_2="2028",
            year_plus_3="2029",
            keywords="bandhani, cargo",
            crafts="Tie-dye",
            sentiment="Bullish"
        )
        self.assertIn("Bandhani Fusion", formatted)
        self.assertIn("Gujarat", formatted)
        self.assertIn("qualitative", formatted.lower())

    def test_pydantic_schema_validation_success(self):
        sample_data = {
            "trends": [
                {
                    "name": "Luxury Minimal Kurta",
                    "category": "Womenswear",
                    "garment": "Raw Silk Kurta",
                    "colour": "Butter Yellow",
                    "material": "Chanderi Silk",
                    "silhouette": "Structured",
                    "aesthetic": "Minimalist",
                    "target_audience": "Urban Youth",
                    "regions": ["Pan India"],
                    "sentiment": "Bullish",
                    "trend_stage": "Growing",
                    "drivers": ["Festive demand"],
                    "evidence": "Observed on runway",
                    "confidence": 0.9,
                    "market_relevance_score": 85.0
                }
            ],
            "market_synthesis": "Positive outlook for minimalist raw silk."
        }
        validated = TrendExtractionResponse(**sample_data)
        self.assertEqual(len(validated.trends), 1)
        self.assertEqual(validated.trends[0].name, "Luxury Minimal Kurta")

    def test_json_cleaner_heuristic(self):
        wrapped_json = "```json\n{\n  \"description\": \"Clean trend\",\n  \"strategic_advice\": \"Invest in craft\"\n}\n```"
        cleaned = self.client._clean_json_response(wrapped_json)
        parsed = json.loads(cleaned)
        self.assertEqual(parsed["description"], "Clean trend")

    def test_deterministic_offline_fallback(self):
        text = "Chikankari embroidered shirts are popular in Delhi."
        keywords = [{"keyword": "chikankari", "score": 1.5}]
        entities = {"indian_crafts": [{"entity": "chikankari", "matched_text": "Chikankari"}]}
        
        fallback_res = self.client._fallback_trend_extraction(
            text=text,
            region="North India",
            year="2026",
            keywords=keywords,
            entities=entities
        )
        self.assertIn("trends", fallback_res)
        self.assertTrue(len(fallback_res["trends"]) > 0)
        self.assertIn("Chikankari", fallback_res["trends"][0]["name"])


if __name__ == "__main__":
    unittest.main()
