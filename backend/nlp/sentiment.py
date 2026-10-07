"""
Fashion Domain Sentiment & Adoption Context Analyzer.
Evaluates trend momentum sentiment, commercial adoption sentiment,
and stylistic tone from fashion text.
"""

from typing import Dict, Any, List


BULLISH_FASHION_TERMS = {
    "viral": 1.5, "surging": 1.4, "breakout": 1.4, "trending": 1.3,
    "must-have": 1.3, "coveted": 1.3, "ubiquitous": 1.2, "statement": 1.2,
    "dominant": 1.3, "favorite": 1.2, "beloved": 1.2, "revival": 1.3,
    "renaissance": 1.3, "essential": 1.2, "bestseller": 1.4, "iconic": 1.3,
    "revolutionizing": 1.3, "freshest": 1.2, "modernized": 1.2
}

BEARISH_FASHION_TERMS = {
    "outdated": -1.4, "declining": -1.3, "passé": -1.4, "fading": -1.3,
    "saturating": -1.2, "fatigue": -1.3, "overdone": -1.3, "overexposed": -1.2,
    "discounted": -1.1, "waning": -1.2, "obsolete": -1.4, "dying": -1.3
}

CONTEXT_CATEGORIES = {
    "Runway & Haute Couture": ["couture", "runway", "designer", "atelier", "fashion week", "luxury", "showstopper"],
    "Streetwear & Youth Culture": ["streetwear", "sneaker", "gen-z", "college", "oversized", "hoodie", "casual"],
    "Festive & Wedding Occasionwear": ["festive", "diwali", "wedding", "bridal", "sangeet", "trousseau", "celebration"],
    "Sustainable & Handloom Craft": ["handloom", "sustainable", "artisan", "organic", "khadi", "handcrafted", "zero waste"]
}


class FashionSentimentAnalyzer:
    """Analyzes market momentum and stylistic context of fashion text."""

    def analyze(self, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "sentiment": "Neutral",
                "momentum_score": 50,
                "confidence": 0.5,
                "detected_tones": [],
                "context_signals": []
            }

        text_lower = text.lower()
        bullish_matches = []
        bearish_matches = []
        score = 50.0  # Base neutral

        for term, weight in BULLISH_FASHION_TERMS.items():
            if term in text_lower:
                bullish_matches.append(term)
                score += (weight * 10)

        for term, weight in BEARISH_FASHION_TERMS.items():
            if term in text_lower:
                bearish_matches.append(term)
                score += (weight * 10)  # weight is negative

        # Clamp score between 0 and 100
        score = max(5.0, min(95.0, score))

        if score >= 65:
            sentiment_label = "Bullish / Accelerating Demand"
        elif score <= 35:
            sentiment_label = "Bearish / Market Fatigue"
        else:
            sentiment_label = "Neutral / Stable Interest"

        # Detect fashion context categories
        context_signals = []
        for context_name, keywords in CONTEXT_CATEGORIES.items():
            hits = [kw for kw in keywords if kw in text_lower]
            if hits:
                context_signals.append({
                    "context": context_name,
                    "matched_indicators": hits,
                    "strength": round(len(hits) / len(keywords), 2)
                })

        return {
            "sentiment": sentiment_label,
            "momentum_score": round(score, 1),
            "bullish_signals": bullish_matches,
            "bearish_signals": bearish_matches,
            "context_signals": context_signals
        }
