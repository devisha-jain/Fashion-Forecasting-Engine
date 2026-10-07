"""
Scoring module for Fashion Trend Intelligence.
Computes transparent composite trend scores combining Google Trends momentum,
NLP prominence, semantic confidence, sentiment valence, and source diversity.
"""

from .trend_scorer import FashionTrendScorer

__all__ = ["FashionTrendScorer"]
