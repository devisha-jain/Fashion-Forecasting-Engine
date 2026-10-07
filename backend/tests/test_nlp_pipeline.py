"""
Unit Tests for Fashion NLP Pipeline and Intelligence Scoring.
"""

import unittest
import sys
import os

# Include backend directory in path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from nlp.preprocessing import FashionTextPreprocessor
from nlp.keyword_extractor import FashionKeywordExtractor
from nlp.entity_extractor import FashionEntityExtractor
from nlp.sentiment import FashionSentimentAnalyzer
from scoring.trend_scorer import FashionTrendScorer
from llm.prompt_loader import PromptLoader


class TestFashionNLPPipeline(unittest.TestCase):

    def setUp(self):
        self.sample_text = (
            "At Lakme Fashion Week 2026, designers showcased oversized handloom kurtas paired with "
            "bandhani cargo pants in butter yellow and chai brown palettes. The indo-western fusion "
            "aesthetic is surging among Gen-Z urban youth seeking comfortable festive wear made with "
            "organic cotton and chanderi silk."
        )
        self.preprocessor = FashionTextPreprocessor()
        self.kw_extractor = FashionKeywordExtractor()
        self.entity_extractor = FashionEntityExtractor()
        self.sentiment_analyzer = FashionSentimentAnalyzer()
        self.scorer = FashionTrendScorer()
        self.prompt_loader = PromptLoader()

    def test_preprocessing(self):
        res = self.preprocessor.process(self.sample_text)
        self.assertIn("cleaned_text", res)
        self.assertTrue(len(res["tokens"]) > 10)
        self.assertTrue(res["statistics"]["lexical_diversity"] > 0)
        self.assertIn("kurta", res["lemmatized_tokens"])

    def test_keyword_extraction(self):
        kws = self.kw_extractor.extract_keywords(self.sample_text, top_k=10)
        self.assertTrue(len(kws) > 0)
        kw_names = [k["keyword"] for k in kws]
        self.assertTrue(any("kurta" in k or "bandhani" in k or "yellow" in k for k in kw_names))

    def test_entity_recognition(self):
        entities = self.entity_extractor.extract_entities(self.sample_text)
        self.assertIn("garments", entities)
        self.assertIn("indian_crafts", entities)
        self.assertIn("fabrics", entities)
        self.assertIn("colors", entities)
        self.assertTrue(any(e["entity"] == "bandhani" for e in entities["indian_crafts"]))
        self.assertTrue(any(e["entity"] == "chanderi" for e in entities["indian_crafts"]))

    def test_sentiment_analysis(self):
        sentiment = self.sentiment_analyzer.analyze(self.sample_text)
        self.assertTrue(sentiment["momentum_score"] >= 50)
        self.assertIn("surging", sentiment["bullish_signals"])

    def test_trend_scoring(self):
        score_res = self.scorer.compute_score(
            gt_momentum=80,
            nlp_prominence=75,
            semantic_confidence=85,
            sentiment_valence=70,
            source_count=3
        )
        self.assertTrue(0 <= score_res["trend_score"] <= 100)
        self.assertIn(score_res["trend_stage"], ["Emerging", "Growing", "Stable", "Declining"])

    def test_prompt_loader(self):
        template = self.prompt_loader.get_template("trend_extraction")
        self.assertIn("OUTPUT SCHEMA", template)
        formatted = self.prompt_loader.format_prompt(
            "trend_extraction",
            text="sample",
            region="North India",
            year="2026",
            keywords="kurta",
            entities="crafts: bandhani"
        )
        self.assertIn("North India", formatted)


if __name__ == "__main__":
    unittest.main()
