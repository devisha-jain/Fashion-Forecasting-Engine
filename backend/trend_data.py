"""
Local Fashion Trend Data Module.
Provides lightweight, local retrieval and caching of search interest trajectories
from trend_cache.json without external network calls or scraping dependencies.
"""

import os
import json
import math
import hashlib
from typing import List, Dict, Any, Optional

CACHE_FILENAME = "trend_cache.json"


def _resolve_cache_path() -> str:
    """
    Resolves the absolute path to trend_cache.json.
    Searches in current directory, parent directory (project root), or working directory.
    """
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILENAME),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CACHE_FILENAME),
        os.path.join(os.getcwd(), CACHE_FILENAME),
        os.path.join(os.getcwd(), "backend", CACHE_FILENAME)
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Default to current directory if not found yet
    return candidates[0]


def _generate_mock_trajectory(keyword: str, region: str = "IN") -> List[int]:
    """
    Generates a structurally valid, realistic 12-month fashion interest trajectory
    [month_1 ... month_12] between 20 and 95. Deterministic for the same keyword
    so it provides consistent data without crashing the application.
    """
    norm_key = (keyword or "fashion").strip().lower()
    # Compute deterministic seed from keyword and region
    seed_hash = int(hashlib.md5(f"{norm_key}:{region}".encode("utf-8")).hexdigest()[:8], 16)
    
    base_level = 45 + (seed_hash % 25)  # 45 - 70 base
    amplitude = 12 + ((seed_hash >> 4) % 15)  # 12 - 27 amplitude
    phase_shift = (seed_hash >> 8) % 12  # 0 - 11 phase

    trajectory: List[int] = []
    for month in range(12):
        # Generate smooth seasonal wave curve
        cycle = math.sin((month + phase_shift) * (math.pi / 6.0))
        # Add slight pseudo-random micro-variation
        noise = (((seed_hash + (month * 17)) % 11) - 5)
        score = int(round(base_level + (amplitude * cycle) + noise))
        # Clamp strictly between 15 and 98
        score = max(15, min(98, score))
        trajectory.append(score)

    return trajectory


def get_trend_interest(keyword: str, region: str = "IN", timeframe: str = "today 12-m") -> List[int]:
    """
    Checks if keyword exists in the local JSON cache (trend_cache.json).
    If it does, returns the historical search array.
    If it doesn't, returns a structurally valid mock array of 12 numbers
    representing the monthly interest trajectory so the app never crashes.
    """
    if not keyword or not str(keyword).strip():
        return _generate_mock_trajectory("fashion", region=region)

    clean_key = str(keyword).strip().lower()
    cache_path = _resolve_cache_path()

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                # Direct match
                if clean_key in data:
                    val = data[clean_key]
                    if isinstance(val, list) and len(val) > 0 and all(isinstance(x, (int, float)) for x in val):
                        return [int(x) for x in val]

                # Case-insensitive / whitespace match check
                for k, val in data.items():
                    if k.strip().lower() == clean_key:
                        if isinstance(val, list) and len(val) > 0:
                            return [int(x) for x in val]
        except Exception:
            # Tolerant of read errors / corrupted JSON
            pass

    # Fallback to structurally valid 12-month array
    return _generate_mock_trajectory(clean_key, region=region)


def update_local_cache(keyword: str, data: List[int]) -> bool:
    """
    Safely appends or updates trend data arrays back into trend_cache.json.
    Ensures safe formatting, atomic writes, and avoids file corruption.
    """
    if not keyword or not str(keyword).strip():
        return False

    if not isinstance(data, list) or len(data) == 0:
        return False

    clean_key = str(keyword).strip().lower()
    clean_data = [int(x) for x in data if isinstance(x, (int, float))]
    if not clean_data:
        return False

    cache_path = _resolve_cache_path()

    # Load existing cache
    existing_cache: Dict[str, Any] = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    existing_cache = loaded
        except Exception:
            existing_cache = {}

    # Append / update keyword
    existing_cache[clean_key] = clean_data

    # Safely write back to file
    try:
        os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
        temp_path = f"{cache_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(existing_cache, f, indent=2, ensure_ascii=False)
        
        # Atomic replace
        os.replace(temp_path, cache_path)
        return True
    except Exception:
        # Fallback standard write
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(existing_cache, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False


# Compatibility bridge for existing backend modules (trend_engine.py)
def get_live_trends(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Compatibility wrapper for trend_engine.
    Maps local trend search interest to the expected dictionary format.
    """
    q = (query or "fashion").strip().lower()
    trajectory = get_trend_interest(q)
    latest_score = trajectory[-1] if trajectory else 65

    return {
        "google": {
            q: latest_score,
            f"{q} India": min(100, latest_score + 4),
            f"{q} fashion": max(10, latest_score - 3),
            f"{q} outfit ideas": min(100, latest_score + 6)
        },
        "trajectory": trajectory,
        "status": "local_cache"
    }


if __name__ == "__main__":
    # Self-test demonstration
    print("=== Testing trend_data.py ===")
    
    # 1. Existing cached keyword
    cached_data = get_trend_interest("streetwear")
    print(f"Cached 'streetwear' interest (12 months): {cached_data}")

    # 2. Non-cached keyword -> Generates 12-item trajectory
    new_data = get_trend_interest("metallic velvet lehenga")
    print(f"Non-cached 'metallic velvet lehenga' trajectory (12 numbers): {new_data}")
    print(f"Length: {len(new_data)}")

    # 3. Update local cache
    updated = update_local_cache("metallic velvet lehenga", [55, 58, 62, 65, 70, 75, 80, 85, 90, 86, 80, 75])
    print(f"Cache update successful: {updated}")

    # 4. Read back updated key
    re_read = get_trend_interest("metallic velvet lehenga")
    print(f"Re-read 'metallic velvet lehenga' from cache: {re_read}")
