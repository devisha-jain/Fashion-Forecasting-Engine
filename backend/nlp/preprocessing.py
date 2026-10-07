"""
Fashion Text Preprocessor.
Handles text cleaning, tokenization, custom fashion stopword filtering,
and linguistic feature extraction.
"""

import re
import unicodedata
from typing import List, Dict, Any, Set


# Standard English stopwords augmented with non-informative web/filler terms
DEFAULT_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've",
    "were", "weren't", "what", "what's", "when", "when's", "where", "where's",
    "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
    "yours", "yourself", "yourselves", "also", "just", "like", "get", "make",
    "look", "see", "one", "new", "via", "click", "read", "post", "share", "com",
    "http", "https", "www"
}

# Domain lemmatization mapping for common fashion plurals and variations
FASHION_LEMMA_MAP: Dict[str, str] = {
    "kurtas": "kurta",
    "kurtis": "kurti",
    "sarees": "saree",
    "saris": "saree",
    "lehengas": "lehenga",
    "lehngas": "lehenga",
    "dupattas": "dupatta",
    "palazzos": "palazzo",
    "anarkalis": "anarkali",
    "dhotis": "dhoti",
    "sherwanis": "sherwani",
    "juttis": "jutti",
    "mojris": "mojri",
    "cholis": "choli",
    "jackets": "jacket",
    "blazers": "blazer",
    "dresses": "dress",
    "skirts": "skirt",
    "trousers": "trouser",
    "pants": "pant",
    "silhouettes": "silhouette",
    "fabrics": "fabric",
    "textiles": "textile",
    "aesthetics": "aesthetic",
    "colors": "color",
    "colours": "colour",
    "patterns": "pattern",
    "prints": "print",
    "embellishments": "embellishment",
    "trends": "trend",
    "stylings": "styling",
    "outfits": "outfit",
    "garments": "garment",
    "handlooms": "handloom",
    "weaves": "weave"
}


class FashionTextPreprocessor:
    """Preprocesses fashion texts for linguistic and TF-IDF extraction."""

    def __init__(self, custom_stopwords: Set[str] = None):
        self.stopwords = DEFAULT_STOPWORDS.copy()
        if custom_stopwords:
            self.stopwords.update(custom_stopwords)

    def clean_text(self, text: str) -> str:
        """Removes URLs, HTML tags, excess whitespace, and normalizes unicode."""
        if not text:
            return ""
        # Unicode normalization (NFKD)
        text = unicodedata.normalize("NFKD", text)
        # Remove URLs
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        # Remove HTML tags
        text = re.sub(r"<.*?>", " ", text)
        # Remove special characters while preserving hyphens within words (e.g. co-ord, indo-western)
        text = re.sub(r"[^\w\s\-]", " ", text)
        # Collapse multiple whitespaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """Extracts word tokens while preserving compound fashion terms."""
        cleaned = self.clean_text(text).lower()
        tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9]\b|\b[a-zA-Z]\b", cleaned)
        return tokens

    def lemmatize_token(self, token: str) -> str:
        """Applies fashion-domain lemmatization rule dictionary."""
        if token in FASHION_LEMMA_MAP:
            return FASHION_LEMMA_MAP[token]
        # Basic suffix heuristics
        if token.endswith("ies") and len(token) > 4:
            return token[:-3] + "y"
        if token.endswith("es") and len(token) > 4 and not token.endswith(("sses", "ches", "shes")):
            return token[:-1]
        if token.endswith("s") and len(token) > 3 and not token.endswith(("ss", "us", "is")):
            return token[:-1]
        return token

    def process(self, text: str) -> Dict[str, Any]:
        """
        Executes full preprocessing pipeline and extracts linguistic profile.
        """
        raw_length = len(text)
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        
        filtered_tokens = []
        lemmatized_tokens = []
        for t in tokens:
            if t not in self.stopwords and len(t) > 1:
                filtered_tokens.append(t)
                lemmatized_tokens.append(self.lemmatize_token(t))

        unique_tokens = set(lemmatized_tokens)
        lexical_diversity = (len(unique_tokens) / len(filtered_tokens)) if filtered_tokens else 0.0
        avg_word_length = (sum(len(w) for w in filtered_tokens) / len(filtered_tokens)) if filtered_tokens else 0.0

        return {
            "cleaned_text": cleaned,
            "normalized_text": " ".join(lemmatized_tokens),
            "tokens": tokens,
            "filtered_tokens": filtered_tokens,
            "lemmatized_tokens": lemmatized_tokens,
            "statistics": {
                "raw_char_count": raw_length,
                "clean_char_count": len(cleaned),
                "total_words": len(tokens),
                "filtered_word_count": len(filtered_tokens),
                "vocabulary_size": len(unique_tokens),
                "lexical_diversity": round(lexical_diversity, 3),
                "average_word_length": round(avg_word_length, 2)
            }
        }
