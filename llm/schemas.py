from __future__ import annotations
"""
Pydantic Schemas for Structured LLM Outputs.
Enforces strict type contracts, anti-hallucination fields, and validation.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class YearlyForecastPoint(BaseModel):
    year: str = Field(default="2026", description="Year label (e.g. 2025, 2026)")
    score: float = Field(default=75.0, ge=0.0, le=100.0, description="Adoption index score 0-100")


class ExtractedTrendItem(BaseModel):
    name: str = Field(default="Contemporary Fashion Movement", description="Distinct trend name")
    category: str = Field(default="Womenswear / Fusion", description="Apparel category")
    garment: str = Field(default="Co-ord / Silhouette", description="Primary garment silhouette")
    colour: str = Field(default="Earth Tones", description="Dominant color or palette direction")
    material: str = Field(default="Handloom Cotton", description="Dominant fabric/fabrication")
    silhouette: str = Field(default="Relaxed Fit", description="Key silhouette descriptors")
    aesthetic: str = Field(default="Indo-Western Fusion", description="Aesthetic core")
    target_audience: str = Field(default="Gen-Z / Urban Youth", description="Target consumer segment")
    regions: List[str] = Field(default_factory=lambda: ["Pan India"], description="Indian geographic relevance")
    sentiment: str = Field(default="Bullish", description="Adoption sentiment")
    trend_stage: str = Field(default="Growing", description="Emerging | Growing | Stable | Declining")
    drivers: List[str] = Field(default_factory=list, description="Key socio-cultural or commercial drivers")
    evidence: str = Field(default="", description="Direct quote or grounded textual evidence")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score")
    market_relevance_score: Optional[float] = Field(default=75.0, description="Market relevance score 0-100")
    palette: List[str] = Field(default_factory=list, description="4 Hex color codes for the trend palette, e.g. ['#E0A96D', '#201E20', '#DDC3A5', '#EEF5DB']")
    description: Optional[str] = Field(default="", description="In-depth trend description tailored to Indian fashion")
    strategic_advice: Optional[str] = Field(default="", description="Actionable merchandising and styling direction")
    consumer_drivers: List[str] = Field(default_factory=list, description="Specific consumer drivers")
    risks: Optional[str] = Field(default="", description="Commercial or material risks")
    peak_season: Optional[str] = Field(default="Festive Q3-Q4", description="Peak commercial retail season")
    target_demographic: Optional[str] = Field(default="Urban Youth (18-30)", description="Primary demographic target")
    competitor_activity: Optional[str] = Field(default="", description="Industry response and designer movements")
    demographics: Dict[str, int] = Field(default_factory=lambda: {"Gen-Z": 60, "Millennials": 30, "Gen-X": 10}, description="Demographic age split percentages summing to 100")
    yearly_forecast: List[YearlyForecastPoint] = Field(default_factory=list, description="5-year adoption projection points")


class TrendExtractionResponse(BaseModel):
    trends: List[ExtractedTrendItem] = Field(default_factory=list, description="Extracted fashion trends")
    market_synthesis: str = Field(default="", description="Executive summary for Indian apparel brands")


class SignalForecastResponse(BaseModel):
    trends: List[ExtractedTrendItem] = Field(default_factory=list, description="AI-generated fashion forecast trend cards")


class TrendAnalysisResponse(BaseModel):
    description: str = Field(default="", description="Rich fashion description tailored to Indian market")
    strategic_advice: str = Field(default="", description="Actionable design and merchandising advice")
    consumer_drivers: List[str] = Field(default_factory=list, description="Key drivers powering this movement")
    risks: str = Field(default="", description="Potential commercial or material risks")
    peak_season: str = Field(default="Festive Q3-Q4", description="Peak commercial retail season")
    target_demographic: str = Field(default="Urban Youth (18-30)", description="Primary demographic target")
    competitor_activity: str = Field(default="", description="Industry response and designer movements")


class ForecastTrajectoryResponse(BaseModel):
    yearly_forecast: List[YearlyForecastPoint] = Field(default_factory=list, description="5-year trajectory")
    forecast_rationale: str = Field(default="", description="Adoption curve explanation")
    demographic_split: Dict[str, float] = Field(default_factory=dict, description="Age bracket breakdown")
    dominant_color_palette: List[str] = Field(default_factory=list, description="Hex color codes")
