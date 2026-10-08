"""
Flask Application Entrypoint for Fashion Trend Intelligence & Forecasting System.
Provides REST API endpoints for multi-signal forecasting, NLP text analysis,
and safe system configuration with Redis caching.
"""

import os
import sys
import time

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import json
import hashlib
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    import yaml
except ImportError:
    yaml = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from trend_engine import generate_forecast, analyze_fashion_text

app = Flask(__name__)

# Restrict CORS to ALLOWED_ORIGINS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins != "*":
    origins = [origin.strip() for origin in allowed_origins.split(",")]
    CORS(app, origins=origins)
    print(f"[INFO] CORS enabled for origins: {origins}")
else:
    CORS(app, origins="*")
    print("[INFO] CORS enabled for all origins (*)")

# Load config.yaml if available (checks backend/config first, then root/config)
config_path = os.path.join(backend_dir, "config", "config.yaml")
if not os.path.exists(config_path):
    config_path = os.path.join(os.path.dirname(backend_dir), "config", "config.yaml")

app_config = {}
if yaml and os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            app_config = yaml.safe_load(f) or {}
            print(f"[INFO] Loaded configuration from {config_path}")
    except Exception as e:
        print(f"[WARN] Failed to load config.yaml: {e}")

# Connect to Redis Cache (optional — runs gracefully without it)
try:
    import redis
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        upstash_url = os.getenv("UPSTASH_REDIS_URL")
        upstash_token = os.getenv("UPSTASH_REDIS_TOKEN")
        if upstash_url and upstash_token:
            clean_url = upstash_url.strip().strip('"').strip("'")
            clean_token = upstash_token.strip().strip('"').strip("'")
            scheme = "rediss" if "rediss" in clean_url else "redis"
            host_port = clean_url.split("://", 1)[-1]
            redis_url = f"{scheme}://default:{clean_token}@{host_port}"
        else:
            redis_url = "redis://localhost:6379"
            
    cache = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=1)
    cache.ping()
    print("[INFO] Connected to Redis Cache successfully.")
except Exception as e:
    print(f"[INFO] Redis not available ({e}). Running in deterministic in-memory mode.")
    cache = None

CACHE_TTL = app_config.get("caching", {}).get("ttl_seconds", 86400)
MAX_TEXT_LEN = app_config.get("nlp", {}).get("max_text_length", 10000)


def get_cache_key(prefix: str, payload_str: str) -> str:
    """Generate MD5 hashed unique cache key."""
    return f"{prefix}:{hashlib.md5(payload_str.encode('utf-8')).hexdigest()}"


def cache_get(cache_key: str, t_start: float):
    """Return (payload, retrieval_latency_ms) on a cache hit, otherwise (None, None)."""
    if not cache:
        return None, None
    try:
        cached = cache.get(cache_key)
        if cached:
            latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
            print(f"[CACHE HIT] {cache_key} ({latency_ms}ms)")
            return json.loads(cached), latency_ms
    except Exception as e:
        print(f"[WARN] Cache read error: {e}")
    return None, None


def cache_set(cache_key: str, payload) -> None:
    """Write a payload to the cache (no-op when Redis is unavailable)."""
    if not (cache and payload):
        return
    try:
        cache.set(cache_key, json.dumps(payload), ex=CACHE_TTL)
        print(f"[CACHE WRITE] {cache_key} (TTL: {CACHE_TTL}s)")
    except Exception as e:
        print(f"[WARN] Cache write error: {e}")


def get_json_body():
    """Parse the request JSON body, tolerating malformed payloads."""
    try:
        return request.get_json(silent=True) or {}
    except Exception:
        return {}


@app.route("/", methods=["GET"])
def home():
    """Root JSON endpoint showing backend NLP & LLM system status."""
    return jsonify({
        "status": "active",
        "system": "AI-Powered Fashion Trend Intelligence & Forecasting System",
        "academic_discipline": "Natural Language Processing (NLP) & Large Language Models (LLM)",
        "framework": "Flask / Python 3.12",
        "llm_engine": f"Google Gemini API ({app_config.get('llm', {}).get('model', 'gemini-2.5-flash')})",
        "nlp_pipeline": {
            "modules": ["Preprocessing", "TF-IDF Keyword Extraction", "Named Entity Recognition", "Fashion Sentiment Analysis", "Trend Intelligence Scoring"],
            "status": "online"
        },
        "endpoints": {
            "GET /": "System health and academic overview",
            "POST /api/forecast": "Interactive multi-signal fashion forecasting",
            "POST /api/analyze": "Dedicated NLP article & text analysis engine",
            "GET /api/config": "System configuration parameters"
        }
    })


@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns strictly safe, non-sensitive configuration settings for UI clients."""
    safe_config = {
        "system": app_config.get("system", {
            "name": "AI-Powered Fashion Trend Intelligence & Forecasting System",
            "version": "2.0.0",
            "academic_discipline": "Natural Language Processing (NLP) & Large Language Models (LLM)"
        }),
        "llm": {
            "provider": app_config.get("llm", {}).get("provider", "google"),
            "model": app_config.get("llm", {}).get("model", "gemini-2.5-flash"),
            "temperature": app_config.get("llm", {}).get("temperature", 0.2),
            "max_output_tokens": app_config.get("llm", {}).get("max_output_tokens", 2048),
            "retry_count": app_config.get("llm", {}).get("retry_count", 2)
        },
        "nlp": app_config.get("nlp", {
            "max_text_length": 10000,
            "keyword_limit": 15
        }),
        "forecasting": app_config.get("forecasting", {
            "default_region": "Pan India",
            "default_year": "2026"
        }),
        "caching": {
            "enabled": app_config.get("caching", {}).get("enabled", True),
            "ttl_seconds": app_config.get("caching", {}).get("ttl_seconds", 86400),
            "engine": "redis" if cache is not None else "in-memory-fallback"
        }
    }
    return jsonify({
        "config": safe_config,
        "features": {
            "redis_caching": cache is not None,
            "gemini_llm": bool(os.getenv("GEMINI_API_KEY")),
            "unsplash_images": bool(os.getenv("UNSPLASH_ACCESS_KEY"))
        }
    })


@app.route("/api/forecast", methods=["POST"])
def api_forecast():
    """JSON API endpoint for multi-signal forecasting with Redis caching."""
    t_start = time.perf_counter()
    data = get_json_body()

    region = data.get("region", "Pan India")
    year = data.get("year", "2026")
    signals = data.get("signals", [])

    query_signal = request.args.get("signal") or request.args.get("query")
    if query_signal:
        if not isinstance(signals, list):
            signals = []
        if query_signal not in signals:
            signals.append(query_signal)

    if not signals:
        return jsonify({"error": "No trend signals selected"}), 400

    raw_cache_payload = f"forecast:{region}:{year}:{','.join(sorted(signals))}:{query_signal or ''}"
    cache_key = get_cache_key("forecast", raw_cache_payload)

    cached_forecasts, cached_latency_ms = cache_get(cache_key, t_start)
    if cached_forecasts is not None:
        return jsonify({
            "forecasts": cached_forecasts,
            "cached": True,
            "latency_ms": cached_latency_ms
        })

    try:
        forecasts = generate_forecast(region=region, year=year, signals=signals, query=query_signal)
    except Exception:
        print("[ERROR] generate_forecast failed:")
        traceback.print_exc()
        forecasts = []

    cache_set(cache_key, forecasts)

    total_latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
    return jsonify({"forecasts": forecasts, "cached": False, "latency_ms": total_latency_ms})


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Dedicated NLP + LLM Fashion Text Analysis API.
    Accepts raw text, executes NLP pipeline and Gemini semantic extraction, and returns structured intelligence.
    """
    t_start = time.perf_counter()
    data = get_json_body()

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON request body. Expected a JSON object."}), 400

    text = str(data.get("text", "")).strip()
    region = str(data.get("region", "Pan India"))
    year = str(data.get("year", "2026"))

    if not text:
        return jsonify({"error": "No input text provided for analysis"}), 400

    if len(text) > MAX_TEXT_LEN:
        return jsonify({"error": f"Input text exceeds maximum allowed limit of {MAX_TEXT_LEN} characters"}), 400

    raw_cache_payload = f"analyze:{region}:{year}:{text}"
    cache_key = get_cache_key("analyze", raw_cache_payload)

    cached_result, cached_latency_ms = cache_get(cache_key, t_start)
    if cached_result is not None:
        metadata = cached_result.setdefault("metadata", {})
        metadata["cached"] = True
        metadata["retrieval_latency_ms"] = cached_latency_ms
        return jsonify(cached_result)

    try:
        analysis_result = analyze_fashion_text(text=text, region=region, year=year)
    except Exception as ex:
        print("[ERROR] analyze_fashion_text failed:")
        traceback.print_exc()
        return jsonify({"error": "Analysis pipeline failure", "details": str(ex)}), 500

    cache_set(cache_key, analysis_result)

    return jsonify(analysis_result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Starting Fashion Forecasting Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

