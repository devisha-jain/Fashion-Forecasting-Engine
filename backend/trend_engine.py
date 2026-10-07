"""
Fashion Trend Intelligence & Forecasting Engine.
Integrates NLP linguistic pipeline, Gemini LLM semantic analysis,
Google Trends live momentum, and multi-signal composite trend scoring.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from trend_data import get_live_trends
from nlp.analyzer import FashionNLPAnalyzer
from llm.gemini_client import GeminiFashionClient
from scoring.trend_scorer import FashionTrendScorer

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# Curated fallback images from Unsplash (free direct CDN)
_FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600&q=80",
    "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&q=80",
    "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&q=80",
    "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=600&q=80",
    "https://images.unsplash.com/photo-1595777216528-071e0127ccbf?w=600&q=80",
    "https://images.unsplash.com/photo-1598554747436-c9293d6a588f?w=600&q=80",
]

# Initialize singleton engine components
nlp_analyzer = FashionNLPAnalyzer()
llm_client = GeminiFashionClient()
trend_scorer = FashionTrendScorer()


_IMAGES_PER_TREND = 3


def fetch_unsplash_images(query: str) -> List[str]:
    """Fetch portrait fashion photos from Unsplash with reliable fallback."""
    fallback = _FALLBACK_IMAGES[:_IMAGES_PER_TREND]
    if not UNSPLASH_ACCESS_KEY:
        return fallback

    try:
        search_query = urllib.parse.quote(f"{query} fashion India")
        url = (
            f"https://api.unsplash.com/search/photos?query={search_query}"
            f"&per_page={_IMAGES_PER_TREND}&orientation=portrait"
        )
        req = urllib.request.Request(url, headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        results = data.get("results", [])
        return [r["urls"]["regular"] for r in results[:_IMAGES_PER_TREND]] or fallback
    except Exception as e:
        print(f"[WARN] Unsplash fetch error: {e}")
        return fallback


def _parse_year(year: Any, default: int = 2026) -> int:
    """Coerce a year value (str or int) to int, falling back to a default."""
    year_str = str(year)
    return int(year_str) if year_str.isdigit() else default


def _build_yearly_forecast(trend_score: float, year: Any) -> List[Dict[str, Any]]:
    """Multi-year adoption trajectory projection shared by forecast and analyze flows."""
    y_int = _parse_year(year)
    return [
        {"year": str(y_int - 1), "score": round(max(30, trend_score - 14))},
        {"year": str(y_int), "score": round(trend_score)},
        {"year": str(y_int + 1), "score": round(min(98, trend_score + 10))},
        {"year": str(y_int + 2), "score": round(max(40, trend_score - 6))},
        {"year": str(y_int + 3), "score": round(max(30, trend_score - 20))}
    ]


def analyze_fashion_text(text: str, region: str = "Pan India", year: str = "2026") -> Dict[str, Any]:
    """
    Dedicated NLP + LLM analysis pipeline for arbitrary fashion text,
    articles, runway reports, and social media captions.
    """
    import time
    start_total = time.perf_counter()

    # Step 1: Run complete NLP Pipeline
    nlp_results = nlp_analyzer.analyze(text)

    # Step 2: Extract structured trends via Gemini LLM with Pydantic validation
    llm_payload = llm_client.extract_trends_from_text(
        text=text,
        region=region,
        year=year,
        keywords=nlp_results["keywords"],
        entities=nlp_results["entities"]
    )
    llm_data = llm_payload.get("result", {})
    extracted_trends = llm_data.get("trends", [])
    market_synthesis = llm_data.get("market_synthesis", "")

    # Step 3: Score each extracted trend using composite multi-signal formula
    scored_trends = []
    for t in extracted_trends:
        trend_name = t.get("name", "Contemporary Fashion Trend")
        
        # Calculate Google Trends proxy from term presence
        live_gt = 75.0
        try:
            live_trends_data = get_live_trends(trend_name)
            g_scores = live_trends_data.get("google", {})
            if g_scores:
                live_gt = float(list(g_scores.values())[0])
        except Exception:
            live_gt = 72.0

        # Sentiment momentum
        sent_momentum = nlp_results["sentiment"].get("momentum_score", 60.0)
        sem_conf = float(t.get("confidence", 0.85)) * 100.0
        
        # Keyword prominence (average top keyword score)
        kw_scores = [k["score"] for k in nlp_results["keywords"][:5]]
        nlp_prominence = (sum(kw_scores) / len(kw_scores) * 30.0) if kw_scores else 65.0

        score_res = trend_scorer.compute_score(
            gt_momentum=live_gt,
            nlp_prominence=nlp_prominence,
            semantic_confidence=sem_conf,
            sentiment_valence=sent_momentum,
            source_count=3
        )

        # Multi-year trajectory projection
        yearly_forecast = _build_yearly_forecast(score_res["trend_score"], year)

        scored_trend_obj = {
            **t,
            "trend_score": score_res["trend_score"],
            "trend_stage": score_res["trend_stage"],
            "score_breakdown": score_res["breakdown"],
            "yearlyForecast": yearly_forecast,
            "images": fetch_unsplash_images(f"{t.get('aesthetic', '')} {t.get('garment', '')}"),
            "palette": ["#ffefef", "#fdfbf7", "#d2b48c", "#8b5a2b"]
        }
        scored_trends.append(scored_trend_obj)

    total_latency_ms = round((time.perf_counter() - start_total) * 1000, 2)

    return {
        "nlp_analysis": {
            "statistics": nlp_results["statistics"],
            "keywords": nlp_results["keywords"],
            "entities": nlp_results["entities"],
            "entity_summary": nlp_results["entity_summary"],
            "sentiment": nlp_results["sentiment"],
            "nlp_latency_ms": nlp_results["nlp_latency_ms"]
        },
        "trends": scored_trends,
        "market_synthesis": market_synthesis,
        "metadata": {
            "processing_time_ms": total_latency_ms,
            "llm_latency_ms": llm_payload.get("latency_ms", 0),
            "llm_model": llm_payload.get("model", "gemini-3.8-flash"),
            "region": region,
            "year": year,
            "cached": False
        }
    }


def generate_forecast(region: str, year: str, signals: List[str], query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Multi-signal dynamic forecasting engine with real Google Trends & NLP enrichment.
    """
    normalized_signals = []
    for sig in signals:
        clean_sig = sig.lower().strip()
        if "old money" in clean_sig:
            normalized_signals.append("old money aesthetic")
        else:
            normalized_signals.append(sig)
    signals = normalized_signals

    if not query and signals:
        query = signals[-1]
    elif not query:
        query = "fashion"

    live_data = get_live_trends(query)
    google_data = live_data.get("google", {})

    trends = []
    signal_strength = {}
    for sig in signals:
        score = 65
        if query:
            clean_sig = sig.lower()
            if clean_sig in google_data:
                score = google_data[clean_sig]
            elif f"{query} fashion" in google_data:
                score = google_data[f"{query} fashion"]
            elif query in google_data:
                score = google_data[query]
            elif list(google_data.values()):
                score = list(google_data.values())[0]

        signal_strength[sig] = min(98, max(45, int(score)))

    # Curated knowledge base augmented with NLP & LLM semantics
    base_templates = {
        "bollywood": {
            "name": "Luxury Minimal Ethnic",
            "category": "Festive Occasionwear",
            "garment": "Monochrome Raw Silk Kurta & Draped Skirt",
            "material": "Chanderi Silk & Raw Silk",
            "colour": "Ivory & Chai Earth Tones",
            "silhouette": "Structured Minimalist Tailoring",
            "aesthetic": "Indo-Western Quiet Luxury",
            "default_desc": f"Understated, monochrome festive ethnic looks inspired by modern Bollywood styling are experiencing high search velocity in {region} for {year}.",
            "palette": ["#fdfbf7", "#f5f5dc", "#d2b48c", "#8b5a2b"],
            "demographics": {"Gen-Z": 60, "Millennials": 30, "Gen-X": 10},
            "image": "luxury_minimal.png",
            "sources": ["Google Trends Live", "Pinterest Culture Signals"]
        },
        "kpop": {
            "name": "Ethnic Streetwear Fusion",
            "category": "Gen-Z Streetwear",
            "garment": "Cargo Dhoti Pants & Cropped Bandhani Bomber",
            "material": "Organic Handloom Cotton & Modal",
            "colour": "Indigo & Cobalt Blue",
            "silhouette": "Oversized Boxy Silhouette",
            "aesthetic": "Streetwear Fusion",
            "default_desc": f"Youth-driven intersection of Seoul streetwear aesthetics with traditional Indian textiles and baggy cargo drapes.",
            "palette": ["#1a1a2e", "#16213e", "#0f3460", "#e94560"],
            "demographics": {"Gen-Z": 75, "Millennials": 20, "Gen-X": 5},
            "image": "streetwear_fusion.png",
            "sources": ["Google Trends Live", "Instagram Style Feeds"]
        },
        "college": {
            "name": "Campus Desi Core",
            "category": "Youth Casuals",
            "garment": "Short Kurti with Wide-Leg Denim",
            "material": "Mulmul Cotton & Indigo Denim",
            "colour": "Butter Yellow & Indigo Blue",
            "silhouette": "Relaxed Everyday Fit",
            "aesthetic": "Collegecore",
            "default_desc": f"Everyday campus fusion pairing breezy cotton kurtis with wide-leg denims, silver oxidized jewelry, and canvas totes.",
            "palette": ["#fef08a", "#93c5fd", "#3b82f6", "#1e3a8a"],
            "demographics": {"Gen-Z": 85, "Millennials": 12, "Gen-X": 3},
            "image": "college_core.png",
            "sources": ["Google Trends Live", "Campus Search Velocity"]
        },
        "festive": {
            "name": "Contemporary Festive Saree Drapes",
            "category": "Occasionwear",
            "garment": "Pre-Draped Saree with Corset Blouse",
            "material": "Tissue Organza & Satin Silk",
            "colour": "Terracotta & Chrome Gold",
            "silhouette": "Fluid Form-Fitting Drapes",
            "aesthetic": "Modern Festive Craftcore",
            "default_desc": f"High conversion occasionwear bridging time-honored artisanal weaves with ready-to-wear pre-stitched silhouettes.",
            "palette": ["#e07a5f", "#3d405a", "#81b29a", "#f2cc8f"],
            "demographics": {"Gen-Z": 50, "Millennials": 40, "Gen-X": 10},
            "image": "festive_1.jpg",
            "sources": ["Google Trends Live", "Wedding Season Forecast"]
        },
        "regional": {
            "name": "Artisanal Handloom Renaissance",
            "category": "Heritage Slow Fashion",
            "garment": "Ajrakh Overlay Jacket & Khadi Co-ord",
            "material": "Handspun Khadi & Vegetable-Dyed Silk",
            "colour": "Earthy Olive & Rust Red",
            "silhouette": "Structured Layering",
            "aesthetic": "Craftcore Revival",
            "default_desc": f"Resurgence of regional block-printing and hand-weaving techniques repurposed for contemporary urban workwear and casual layering.",
            "palette": ["#588157", "#3a5a40", "#dad7cd", "#a3b18a"],
            "demographics": {"Gen-Z": 45, "Millennials": 45, "Gen-X": 10},
            "image": "regional_handloom.png",
            "sources": ["Google Trends Live", "Textile Guild Reports"]
        }
    }

    for sig in signals:
        sig_lower = sig.lower()
        matched_key = None
        for key in base_templates:
            if key in sig_lower:
                matched_key = key
                break

        if matched_key:
            template = base_templates[matched_key]
        else:
            template = {
                "name": f"{sig.title()} Contemporary Movement",
                "category": "Apparel & Lifestyle",
                "garment": "Modular Fusion Silhouette",
                "material": "Handloom Cotton & Linen",
                "colour": "Earthy Neutrals",
                "silhouette": "Fluid & Tailored",
                "aesthetic": f"{sig.title()} Fusion",
                "default_desc": f"A notable shift towards {sig} across {region} for the {year} market cycle.",
                "palette": ["#cba89a", "#8b5a2b", "#d2b48c", "#50352d"],
                "demographics": {"Gen-Z": 60, "Millennials": 30, "Gen-X": 10},
                "image": "luxury_minimal.png",
                "sources": ["Google Trends Live", "Social Listening"]
            }

        # Query semantic LLM analysis
        llm_analysis = llm_client.analyze_trend_semantics(
            trend_name=template["name"],
            region=region,
            year=year,
            signal_strength=signal_strength,
            signal_type=sig,
            keywords=[template["garment"], template["material"], template["aesthetic"]]
        )

        gt_score = float(signal_strength.get(sig, 70))
        score_res = trend_scorer.compute_score(
            gt_momentum=gt_score,
            nlp_prominence=75.0,
            semantic_confidence=85.0,
            sentiment_valence=70.0,
            source_count=3
        )

        yearly_forecast = _build_yearly_forecast(score_res["trend_score"], year)

        # Fetch 3 dynamic visual images from Unsplash or local gallery
        dynamic_images = fetch_unsplash_images(f"{template['name']} {template['aesthetic']}")

        trend_card = {
            "name": template["name"],
            "category": template["category"],
            "garment": template["garment"],
            "material": template["material"],
            "colour": template["colour"],
            "silhouette": template["silhouette"],
            "aesthetic": template["aesthetic"],
            "confidence": 0.88,
            "trend_score": score_res["trend_score"],
            "trend_stage": score_res["trend_stage"],
            "market_relevance_score": score_res["trend_score"],
            "momentum": f"{score_res['trend_stage']} Momentum ↗",
            "description": llm_analysis.description or template["default_desc"],
            "business": llm_analysis.strategic_advice,
            "strategic_advice": llm_analysis.strategic_advice,
            "consumer_drivers": llm_analysis.consumer_drivers,
            "risks": llm_analysis.risks,
            "targetDemographic": llm_analysis.target_demographic,
            "peakSeason": llm_analysis.peak_season,
            "competitorActivity": llm_analysis.competitor_activity,
            "yearlyForecast": yearly_forecast,
            "score_breakdown": score_res["breakdown"],
            "palette": template["palette"],
            "graph": signal_strength,
            "demographics": template["demographics"],
            "image": template["image"],
            "images": dynamic_images,
            "sources": template["sources"]
        }
        trends.append(trend_card)

    return trends
