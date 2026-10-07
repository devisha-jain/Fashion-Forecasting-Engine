"""
Fashion NLP Pipeline Analyzer.
Orchestrates preprocessing, TF-IDF domain keyword extraction,
Fashion Named Entity Recognition, and sentiment profiling.
"""

import time
from typing import Dict, Any
from .preprocessing import FashionTextPreprocessor
from .keyword_extractor import FashionKeywordExtractor
from .entity_extractor import FashionEntityExtractor
from .sentiment import FashionSentimentAnalyzer


class FashionNLPAnalyzer:
    """End-to-end NLP intelligence engine for fashion discourse."""

    def __init__(self):
        self.preprocessor = FashionTextPreprocessor()
        self.keyword_extractor = FashionKeywordExtractor()
        self.entity_extractor = FashionEntityExtractor()
        self.sentiment_analyzer = FashionSentimentAnalyzer()

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Executes the complete 4-stage NLP pipeline and captures execution time.
        """
        start_time = time.perf_counter()

        # Stage 1: Preprocessing & Linguistic Tokenization
        preprocess_res = self.preprocessor.process(text)

        # Stage 2: TF-IDF & Domain-Weighted Keyword Extraction
        keywords = self.keyword_extractor.extract_keywords(text, top_k=15)

        # Stage 3: Fashion Named Entity Recognition (NER)
        entities = self.entity_extractor.extract_entities(text)
        entity_summary = self.entity_extractor.get_entity_summary(entities)

        # Stage 4: Sentiment & Adoption Context Analysis
        sentiment = self.sentiment_analyzer.analyze(text)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "cleaned_text": preprocess_res["cleaned_text"],
            "normalized_text": preprocess_res["normalized_text"],
            "statistics": preprocess_res["statistics"],
            "keywords": keywords,
            "entities": entities,
            "entity_summary": entity_summary,
            "sentiment": sentiment,
            "nlp_latency_ms": elapsed_ms
        }
