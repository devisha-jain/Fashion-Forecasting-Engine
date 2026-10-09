"""
TF-IDF & Domain-Weighted Fashion Keyword Extractor.
Uses Scikit-Learn TF-IDF vectorization boosted with a curated Indian fashion taxonomy.
"""

from typing import List, Dict, Any, Set
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer


# Curated Indian & Global fashion domain taxonomy for relevance boosting
FASHION_DOMAIN_TAXONOMY: Dict[str, float] = {
    # Indian Regional Craft & Textiles (High Boost 1.5x)
    "chikankari": 1.5,
    "bandhani": 1.5,
    "kanjeevaram": 1.5,
    "banarasi": 1.5,
    "khadi": 1.4,
    "ajrakh": 1.5,
    "phulkari": 1.5,
    "chanderi": 1.4,
    "ikkat": 1.4,
    "kalamkari": 1.4,
    "zardozi": 1.4,
    "gota patti": 1.4,
    "patola": 1.5,
    "mulmul": 1.3,
    "tussar": 1.3,
    "handloom": 1.4,
    "block print": 1.3,

    # Garments & Silhouettes (Boost 1.3x)
    "kurta": 1.3,
    "kurti": 1.3,
    "saree": 1.4,
    "lehenga": 1.4,
    "anarkali": 1.3,
    "dupatta": 1.2,
    "palazzo": 1.2,
    "co-ord": 1.3,
    "dhoti": 1.2,
    "sherwani": 1.3,
    "jacket": 1.2,
    "corset": 1.3,
    "blazer": 1.2,
    "slip dress": 1.2,
    "cargo": 1.3,
    "drape": 1.3,
    "oversized": 1.3,
    "structured": 1.2,
    "asymmetrical": 1.3,
    "maxi": 1.2,

    # Aesthetics & Subcultures (Boost 1.3x)
    "indo-western": 1.4,
    "fusion": 1.3,
    "streetwear": 1.3,
    "minimalist": 1.3,
    "boho": 1.2,
    "craftcore": 1.4,
    "quiet luxury": 1.3,
    "collegecore": 1.3,
    "y2k": 1.3,
    "retro": 1.2,
    "vintage": 1.2,
    "festive": 1.3,
    "wedding": 1.3,
    "sustainable": 1.3,
    "slow fashion": 1.3,

    # Colors & Palettes (Boost 1.2x)
    "butter yellow": 1.4,
    "espresso": 1.3,
    "terracotta": 1.3,
    "sage green": 1.3,
    "chai brown": 1.4,
    "indigo": 1.3,
    "maroon": 1.2,
    "mustard": 1.2,
    "metallic": 1.2,
    "pastel": 1.2,
    "monochrome": 1.2
}


class FashionKeywordExtractor:
    """Extracts domain-relevant keywords using TF-IDF and taxonomy boosting."""

    def __init__(self, max_features: int = 40, ngram_range: tuple = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range

    def _determine_category(self, phrase: str) -> str:
        """Determines the fashion taxonomy category of an extracted keyword."""
        phrase_lower = phrase.lower()
        craft_terms = {"chikankari", "bandhani", "kanjeevaram", "banarasi", "khadi", "ajrakh", "phulkari", "chanderi", "ikkat", "kalamkari", "zardozi", "handloom", "block print"}
        garment_terms = {"kurta", "kurti", "saree", "lehenga", "anarkali", "dupatta", "palazzo", "co-ord", "dhoti", "sherwani", "jacket", "corset", "blazer", "dress", "cargo", "silhouette"}
        aesthetic_terms = {"indo-western", "fusion", "streetwear", "minimalist", "craftcore", "quiet luxury", "collegecore", "y2k", "vintage", "retro", "festive", "sustainable"}
        color_terms = {"yellow", "brown", "green", "espresso", "chai", "terracotta", "indigo", "maroon", "mustard", "metallic", "pastel", "palette", "shade", "hue"}

        for t in craft_terms:
            if t in phrase_lower:
                return "Regional Craft & Textile"
        for t in garment_terms:
            if t in phrase_lower:
                return "Garment & Silhouette"
        for t in aesthetic_terms:
            if t in phrase_lower:
                return "Aesthetic & Style"
        for t in color_terms:
            if t in phrase_lower:
                return "Color & Palette"
        return "Fashion Context"

    def extract_keywords(self, text: str, top_k: int = 15) -> List[Dict[str, Any]]:
        """
        Extracts top-k keywords from input text using TF-IDF weighted by domain taxonomy.
        """
        if not text or len(text.strip()) < 5:
            return []

        # Split text into sentence chunks to create a local corpus for TF-IDF
        sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if len(s.strip()) > 10]
        if len(sentences) < 2:
            # If short text, split by clauses or words to create pseudo-corpus
            sentences = [text]

        try:
            vectorizer = TfidfVectorizer(
                ngram_range=self.ngram_range,
                stop_words="english",
                max_features=self.max_features,
                token_pattern=r"(?u)\b[a-zA-Z\-]{2,}\b"
            )
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.sum(axis=0).A1
            
            raw_keywords = dict(zip(feature_names, scores))
        except Exception:
            # Fallback to pure word frequency if TF-IDF fails on irregular text
            words = [w.lower() for w in text.split() if len(w) > 3]
            counts = Counter(words)
            total = max(1, sum(counts.values()))
            raw_keywords = {k: v / total for k, v in counts.items()}

        # Apply domain taxonomy weights
        weighted_keywords = []
        for phrase, score in raw_keywords.items():
            phrase_clean = phrase.strip().lower()
            if len(phrase_clean) < 2:
                continue
                
            weight_multiplier = 1.0
            for term, multiplier in FASHION_DOMAIN_TAXONOMY.items():
                if term in phrase_clean:
                    weight_multiplier = max(weight_multiplier, multiplier)
                    
            boosted_score = score * weight_multiplier
            category = self._determine_category(phrase_clean)
            weighted_keywords.append({
                "keyword": phrase_clean,
                "score": round(float(boosted_score), 4),
                "raw_tfidf": round(float(score), 4),
                "boost_factor": weight_multiplier,
                "category": category
            })

        # Sort descending by boosted score
        weighted_keywords.sort(key=lambda x: x["score"], reverse=True)
        return weighted_keywords[:top_k]
