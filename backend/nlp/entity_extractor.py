"""
Fashion Named Entity Recognition (NER) Extractor.
Extracts structured fashion entities across 6 domain categories:
- Garments & Silhouettes
- Indian Regional Crafts & Techniques
- Fabrics & Materials
- Aesthetics & Subcultures
- Color Palettes
- Demographics & Regions
"""

import re
from typing import List, Dict, Any, Set


FASHION_ENTITY_DICTIONARIES: Dict[str, List[str]] = {
    "GARMENT_SILHOUETTE": [
        "kurta", "kurti", "saree", "sari", "lehenga", "lehnga", "anarkali",
        "dupatta", "palazzo", "co-ord set", "co-ord", "dhoti", "sherwani",
        "corset", "blazer", "slip dress", "cargo pants", "cargo lehenga",
        "draped skirt", "cape", "asymmetric hem", "oversized shirt", "jacket",
        "trench coat", "sharara", "gharara", "angrakha", "peplum top"
    ],
    "INDIAN_CRAFT_TEXTILE": [
        "chikankari", "bandhani", "kanjeevaram", "banarasi", "khadi",
        "ajrakh", "phulkari", "chanderi", "ikkat", "ikat", "kalamkari",
        "zardozi", "gota patti", "patola", "bagh print", "dabu print",
        "tussar silk", "kasavu", "sambalpuri", "block printing", "handloom"
    ],
    "FABRIC_MATERIAL": [
        "silk", "cotton", "linen", "organza", "velvet", "satin", "georgette",
        "chiffon", "denim", "mulmul", "modal", "crepe", "viscose", "brocade",
        "chambray", "raw silk", "tissue silk", "leather", "knitwear"
    ],
    "AESTHETIC_SUBCULTURE": [
        "indo-western", "craftcore", "quiet luxury", "streetwear fusion",
        "streetwear", "collegecore", "minimalist", "y2k", "vintage revival",
        "boho chic", "maximalism", "festive modernism", "desi core",
        "indie aesthetic", "retro bollywood", "clean girl", "goth fusion"
    ],
    "COLOR_PALETTE": [
        "butter yellow", "chai brown", "espresso", "terracotta", "sage green",
        "dusty rose", "ivory", "indigo", "maroon", "mustard yellow",
        "emerald green", "cobalt blue", "metallic gold", "chrome silver",
        "blush pink", "olive green", "crimson", "nude palette", "earth tones"
    ],
    "DEMOGRAPHIC_REGION": [
        "gen z", "gen-z", "millennials", "urban youth", "tier 1 metros",
        "mumbai", "delhi ncr", "bengaluru", "punjab", "gujarat", "rajasthan",
        "south india", "kolkata", "hyderabad", "working women", "bridal"
    ]
}


class FashionEntityExtractor:
    """Extracts named entities from fashion domain discourse."""

    def __init__(self):
        self.dictionaries = FASHION_ENTITY_DICTIONARIES

    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scans text for domain entities, recording occurrences, character spans,
        and entity categorization.
        """
        if not text:
            return {}

        text_lower = text.lower()
        extracted: Dict[str, List[Dict[str, Any]]] = {
            "garments": [],
            "indian_crafts": [],
            "fabrics": [],
            "aesthetics": [],
            "colors": [],
            "demographics": []
        }

        category_map = {
            "GARMENT_SILHOUETTE": "garments",
            "INDIAN_CRAFT_TEXTILE": "indian_crafts",
            "FABRIC_MATERIAL": "fabrics",
            "AESTHETIC_SUBCULTURE": "aesthetics",
            "COLOR_PALETTE": "colors",
            "DEMOGRAPHIC_REGION": "demographics"
        }

        seen_spans: Set[str] = set()

        for cat_key, terms in self.dictionaries.items():
            target_list_name = category_map[cat_key]
            for term in terms:
                # Use regex word boundaries for precise entity detection
                pattern = r"\b" + re.escape(term) + r"\b"
                for match in re.finditer(pattern, text_lower):
                    start, end = match.span()
                    original_text_slice = text[start:end]
                    span_key = f"{start}:{end}:{term}"
                    
                    if span_key not in seen_spans:
                        seen_spans.add(span_key)
                        extracted[target_list_name].append({
                            "entity": term,
                            "matched_text": original_text_slice,
                            "start": start,
                            "end": end,
                            "category": cat_key
                        })

        # Deduplicate and sort by appearance
        for cat in extracted:
            extracted[cat].sort(key=lambda x: x["start"])

        return extracted

    def get_entity_summary(self, entities: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Creates an aggregated count summary of detected fashion entities."""
        summary = {}
        total_count = 0
        for cat, items in entities.items():
            unique_entities = sorted(list(set(item["entity"].title() for item in items)))
            summary[cat] = {
                "count": len(items),
                "unique_terms": unique_entities
            }
            total_count += len(items)
        summary["total_detected"] = total_count
        return summary
