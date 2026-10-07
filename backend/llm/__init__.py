"""
LLM Module for Gemini Semantic Extraction and Trend Intelligence.
Provides Pydantic schemas, external prompt template management,
and robust API interaction with validation and retry logic.
"""

from .schemas import (
    ExtractedTrendItem,
    TrendExtractionResponse,
    TrendAnalysisResponse,
    YearlyForecastPoint,
    ForecastTrajectoryResponse
)
from .prompt_loader import PromptLoader
from .gemini_client import GeminiFashionClient

__all__ = [
    "ExtractedTrendItem",
    "TrendExtractionResponse",
    "TrendAnalysisResponse",
    "YearlyForecastPoint",
    "ForecastTrajectoryResponse",
    "PromptLoader",
    "GeminiFashionClient"
]
