"""
Pydantic Schemas for Structured LLM Outputs.
Enforces strict type contracts, anti-hallucination fields, and validation.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ExtractedTrendItem(BaseModel):
    name: str = Field(..., description="Distinct trend name")
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


class TrendExtractionResponse(BaseModel):
    trends: List[ExtractedTrendItem] = Field(default_factory=list, description="Extracted fashion trends")
    market_synthesis: str = Field(default="", description="Executive summary for Indian apparel brands")


class TrendAnalysisResponse(BaseModel):
    description: str = Field(..., description="Rich fashion description tailored to Indian market")
    strategic_advice: str = Field(default="", description="Actionable design and merchandising advice")
    consumer_drivers: List[str] = Field(default_factory=list, description="Key drivers powering this movement")
    risks: str = Field(default="", description="Potential commercial or material risks")
    peak_season: str = Field(default="Festive Q3-Q4", description="Peak commercial retail season")
    target_demographic: str = Field(default="Urban Youth (18-30)", description="Primary demographic target")
    competitor_activity: str = Field(default="", description="Industry response and designer movements")


class YearlyForecastPoint(BaseModel):
    year: str = Field(..., description="Year label (e.g. 2025, 2026)")
    score: float = Field(..., ge=0.0, le=100.0, description="Adoption index score 0-100")


class ForecastTrajectoryResponse(BaseModel):
    yearly_forecast: List[YearlyForecastPoint] = Field(default_factory=list, description="5-year trajectory")
    forecast_rationale: str = Field(default="", description="Adoption curve explanation")
    demographic_split: Dict[str, float] = Field(default_factory=dict, description="Age bracket breakdown")
    dominant_color_palette: List[str] = Field(default_factory=list, description="Hex color codes")


class DynamicTrendProfile(BaseModel):
    name: str = Field(..., description="Distinct trend title")
    category: str = Field(default="Womenswear / Contemporary Fusion", description="Apparel category")
    garment: str = Field(default="Co-ord & Modern Silhouette", description="Key garment")
    material: str = Field(default="Handloom Cotton & Silk", description="Fabric and textiles")
    colour: str = Field(default="Earth Tones", description="Color direction")
    silhouette: str = Field(default="Structured Fluid Tailoring", description="Key silhouette")
    aesthetic: str = Field(default="Contemporary Indian Fusion", description="Aesthetic style")
    description: str = Field(default="", description="2-3 sentence trend description")
    strategic_advice: str = Field(default="", description="Strategic merchandising advice")
    consumer_drivers: List[str] = Field(default_factory=list, description="Consumer adoption drivers")
    risks: str = Field(default="", description="Commercial and material risks")
    peak_season: str = Field(default="Festive Q3-Q4", description="Peak season")
    target_demographic: str = Field(default="Urban Youth (18-32)", description="Target demographic")
    competitor_activity: str = Field(default="", description="Competitor and designer response")
    palette: List[str] = Field(default_factory=lambda: ["#2d3748", "#4a5568", "#cbd5e0", "#e2e8f0"], description="Color hex palette")
    demographics: Dict[str, float] = Field(default_factory=lambda: {"Gen-Z": 60, "Millennials": 30, "Gen-X": 10}, description="Demographic breakdown")
    yearly_forecast: List[Dict[str, Any]] = Field(default_factory=list, description="5-year forecast points")
    confidence: float = Field(default=0.88, ge=0.0, le=1.0)
    trend_score: float = Field(default=75.0, ge=0.0, le=100.0)

