"""
Gemini LLM Client for Fashion Trend Intelligence.
Handles API calls with Google GenAI SDK, structured JSON output enforcement,
Pydantic response validation, automatic retry, and model fallbacks.
All fashion forecasts and trend extractions are generated dynamically via Gemini API.
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_env = os.path.join(os.path.dirname(os.path.dirname(current_dir)), ".env")
    if os.path.exists(root_env):
        load_dotenv(root_env)
except ImportError:
    pass

from .prompt_loader import PromptLoader
from .schemas import (
    TrendExtractionResponse,
    TrendAnalysisResponse,
    SignalForecastResponse,
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
        
        raw_key = api_key or os.getenv("GEMINI_API_KEY") or ""
        self.api_key = raw_key.strip().strip('"').strip("'")
        configured_model = model_name or llm_cfg.get("model", "gemini-2.5-flash")
        if "3.8" in configured_model:
            configured_model = "gemini-2.5-flash"
            
        self.model_name = configured_model
        self.fallback_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
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
            print("[WARN] GEMINI_API_KEY not configured in environment.")

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

    def _generate_validated(self, prompt: str, schema, retry_delay: float = 0.5):
        """
        Calls Gemini with candidate model fallbacks and validates JSON reply against a Pydantic schema.
        Raises an error with details if the API fails.
        """
        if not self.is_available or not self.client:
            raise RuntimeError(
                "Gemini API key is not configured or client failed to initialize. "
                "Please configure a valid GEMINI_API_KEY in your .env file."
            )

        # Build prioritized candidate models
        candidate_models = [self.model_name]
        for m in self.fallback_models:
            if m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for model in candidate_models:
            for attempt in range(max(1, self.retry_count)):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    cleaned = self._clean_json_response(response.text or "")
                    parsed = json.loads(cleaned)
                    result = schema(**parsed)
                    # Cache the working model
                    self.model_name = model
                    return result
                except Exception as e:
                    last_error = e
                    time.sleep(retry_delay)

        raise RuntimeError(f"Gemini API error ({self.model_name}): {last_error}")

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

        validated = self._generate_validated(prompt, TrendExtractionResponse, retry_delay=0.4)
        return {
            "result": validated.model_dump(),
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "model": self.model_name,
            "validated": True
        }

    def generate_forecast_cards(
        self,
        signals: List[str],
        region: str = "Pan India",
        year: str = "2026",
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates bespoke fashion forecasting trend cards directly via Gemini API.
        No hardcoded base templates or dummy cards are used.
        """
        y_int = int(year) if str(year).isdigit() else 2026
        signals_str = ", ".join(signals) if signals else (query or "contemporary fashion")
        primary_query = query or (signals[-1] if signals else "contemporary fashion")

        prompt = self.prompt_loader.format_prompt(
            "signal_forecast",
            region=region,
            year=str(y_int),
            signals=signals_str,
            query=primary_query,
            year_minus_1=str(y_int - 1),
            year_plus_1=str(y_int + 1),
            year_plus_2=str(y_int + 2),
            year_plus_3=str(y_int + 3)
        )

        validated = self._generate_validated(prompt, SignalForecastResponse, retry_delay=0.5)
        raw_trends = [t.model_dump() for t in validated.trends]
        return raw_trends

    def analyze_trend_semantics(
        self,
        trend_name: str,
        region: str = "Pan India",
        year: str = "2026",
        signal_strength: Dict[str, Any] = None,
        signal_type: str = "Cultural Trend",
        keywords: List[str] = None
    ) -> TrendAnalysisResponse:
        """Generates rich commercial trend descriptions and drivers via Gemini."""
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
        return self._generate_validated(prompt, TrendAnalysisResponse, retry_delay=0.4)
