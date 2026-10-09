"""
Gemini LLM Client for Fashion Trend Intelligence.
Handles API calls with Google GenAI SDK, structured JSON output enforcement,
Pydantic response validation, automatic retry, and deterministic fallback.
"""

import os
import json
import re
import time
from typing import Dict, Any, Optional, List

try:
    import yaml
except ImportError:
    yaml = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .prompt_loader import PromptLoader
from .schemas import (
    TrendExtractionResponse,
    TrendAnalysisResponse,
    ForecastTrajectoryResponse,
    ExtractedTrendItem,
    YearlyForecastPoint
)


def _load_system_config() -> Dict[str, Any]:
    """Loads system configuration from config/config.yaml."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    root_dir = os.path.dirname(backend_dir)
    config_path = os.path.join(root_dir, "config", "config.yaml")
    
    if yaml and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    return {}


class GeminiFashionClient:
    """Client for Google Gemini API structured fashion intelligence."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.config = _load_system_config()
        llm_cfg = self.config.get("llm", {})
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or llm_cfg.get("model", "gemini-3.8-flash")
        self.retry_count = int(llm_cfg.get("retry_count", 2))
        self.prompt_loader = PromptLoader()
        self.client = None
        self.is_available = False

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                self.is_available = True
                print(f"[INFO] Gemini LLM Client connected ({self.model_name})")
            except Exception as e:
                print(f"[WARN] Gemini Client initialization failed: {e}")
                self.is_available = False
        else:
            print("[INFO] GEMINI_API_KEY not configured. Running in deterministic heuristic fallback mode.")

    def _clean_json_response(self, text: str) -> str:
        """Extracts and repairs JSON substring from LLM response text."""
        if not text:
            return "{}"
        clean = text.strip()
        # Remove markdown code block syntax
        if "```" in clean:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean)
            if match:
                clean = match.group(1).strip()
        # If still prefixed by json
        if clean.lower().startswith("json"):
            clean = clean[4:].strip()
        # Find outer braces if wrapped in surrounding text
        start_idx = clean.find("{")
        end_idx = clean.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            clean = clean[start_idx:end_idx + 1]
        return clean

    def extract_trends_from_text(
        self,
        text: str,
        region: str = "Pan India",
        year: str = "2026",
        keywords: List[Dict[str, Any]] = None,
        entities: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Extracts structured fashion trends from raw text using Gemini with schema validation.
        """
        start_time = time.perf_counter()
        kw_str = ", ".join([k["keyword"] for k in (keywords or [])[:8]])
        
        ent_str_list = []
        if entities:
            for cat, items in entities.items():
                if isinstance(items, list) and items:
                    terms = list(set([i.get("entity", "") for i in items if isinstance(i, dict)]))
                    if terms:
                        ent_str_list.append(f"{cat}: {', '.join(terms[:4])}")
        ent_str = " | ".join(ent_str_list) if ent_str_list else "None detected"

        prompt = self.prompt_loader.format_prompt(
            "trend_extraction",
            text=text,
            region=region,
            year=year,
            keywords=kw_str,
            entities=ent_str
        )

        if self.is_available and self.client:
            try:
                validated = self._generate_validated(prompt, TrendExtractionResponse, retry_delay=0.5)
                return self._extraction_payload(validated.model_dump(), self.model_name, start_time)
            except Exception as e:
                # If API attempts fail, fail gracefully to NLP heuristic
                print(f"[WARN] Gemini extraction failed ({e}). Using deterministic NLP fallback.")

        # Deterministic NLP-driven heuristic fallback when offline or after API failure
        fallback_res = self._fallback_trend_extraction(text, region, year, keywords, entities)
        return self._extraction_payload(fallback_res, "nlp-heuristic-fallback", start_time)

    def _generate_validated(self, prompt: str, schema, retry_delay: float):
        """
        Calls Gemini with retries and validates the JSON reply against a Pydantic schema.
        Returns the validated model, or re-raises the last error once retries are exhausted.
        """
        last_error = None
        for _ in range(max(1, self.retry_count)):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                parsed = json.loads(self._clean_json_response(response.text or ""))
                return schema(**parsed)
            except Exception as e:
                last_error = e
                time.sleep(retry_delay)
        raise last_error

    @staticmethod
    def _extraction_payload(result: Dict[str, Any], model: str, start_time: float) -> Dict[str, Any]:
        """Wraps an extraction result with latency, model, and validation metadata."""
        return {
            "result": result,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "model": model,
            "validated": True
        }

    def analyze_trend_semantics(
        self,
        trend_name: str,
        region: str = "Pan India",
        year: str = "2026",
        signal_strength: Dict[str, Any] = None,
        signal_type: str = "Cultural Trend",
        keywords: List[str] = None
    ) -> TrendAnalysisResponse:
        """Generates rich commercial trend descriptions and drivers."""
        kw_str = ", ".join(keywords or [trend_name])
        prompt = self.prompt_loader.format_prompt(
            "trend_analysis",
            trend_name=trend_name,
            region=region,
            year=year,
            signal_strength=str(signal_strength or {}),
            signal_type=signal_type,
            keywords=kw_str
        )

        if self.is_available and self.client:
            try:
                return self._generate_validated(prompt, TrendAnalysisResponse, retry_delay=0.4)
            except Exception:
                pass

        return self._fallback_trend_analysis(trend_name, region, year)

    def _fallback_trend_extraction(
        self,
        text: str,
        region: str,
        year: str,
        keywords: List[Dict[str, Any]] = None,
        entities: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Synthesizes structured trends deterministically from NLP entities when Gemini is offline."""
        top_kws = [k["keyword"].title() for k in (keywords or [])[:4]]
        trend_name = f"{top_kws[0]} Modernism" if top_kws else "Contemporary Indian Fusion"
        
        garment = "Co-ord Set & Tailored Silhouette"
        fabric = "Handloom Cotton & Chanderi"
        color = "Butter Yellow & Chai Earth Tones"
        aesthetic = "Indo-Western Craftcore"
        
        if entities:
            if entities.get("garments"):
                garment = entities["garments"][0]["matched_text"].title()
            if entities.get("fabrics"):
                fabric = entities["fabrics"][0]["matched_text"].title()
            if entities.get("colors"):
                color = entities["colors"][0]["matched_text"].title()
            if entities.get("aesthetics"):
                aesthetic = entities["aesthetics"][0]["matched_text"].title()

        sample_trend = ExtractedTrendItem(
            name=trend_name,
            category="Indo-Western Fusion & Streetwear",
            garment=garment,
            colour=color,
            material=fabric,
            silhouette="Relaxed Fluid Silhouette",
            aesthetic=aesthetic,
            target_audience="Urban Gen-Z & Millennials (18-32)",
            regions=[region, "Delhi NCR", "Mumbai", "Bengaluru"],
            sentiment="Bullish / Accelerating Demand",
            trend_stage="Growing",
            drivers=[
                "Festive adaptability with lightweight breathable textiles",
                "Digital aesthetic virality on Instagram & Pinterest",
                "Contemporary redesign of regional artisanal crafts"
            ],
            evidence=f"Textual signals emphasize high interest in {', '.join(top_kws[:3])}.",
            confidence=0.88,
            market_relevance_score=82.0
        )

        return {
            "trends": [sample_trend.model_dump()],
            "market_synthesis": f"In {year}, the Indian apparel market is prioritizing versatile {aesthetic} styles combining {fabric} with functional silhouettes."
        }

    def _fallback_trend_analysis(self, trend_name: str, region: str, year: str) -> TrendAnalysisResponse:
        """Deterministic fallback analysis response."""
        return TrendAnalysisResponse(
            description=f"A high-momentum style movement in {region} for {year}, marrying artisanal Indian handloom heritage with clean contemporary tailoring.",
            strategic_advice="Brands should produce limited-run drops focusing on breathable natural textiles and modular styling.",
            consumer_drivers=[
                "Rising youth demand for heritage craft with modern cuts",
                "Instagram street style and celebrity festive endorsements",
                "Demand for season-transcending versatile wardrobe staples"
            ],
            risks="Price sensitivity on high-grade handloom textiles; rapid fast-fashion copycat cycles.",
            peak_season="Festive & Autumn / Winter",
            target_demographic="Urban youth and young working professionals aged 18–35",
            competitor_activity="Leading boutique D2C labels are integrating these silhouettes into seasonal capsule collections."
        )
