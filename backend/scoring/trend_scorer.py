"""
Composite Fashion Trend Scorer.
Calculates a multi-dimensional transparent Trend Intelligence Score (0–100)
and classifies the trend stage based on weighted signal inputs.
"""

from typing import Dict, Any


class FashionTrendScorer:
    """
    Computes transparent multi-signal trend intelligence scores.
    Formula:
      Trend Score = (Google Trends Momentum * w_gt)
                  + (NLP Keyword Prominence * w_nlp)
                  + (Semantic LLM Confidence * w_sem)
                  + (Sentiment Valence * w_sent)
                  + (Source Diversity * w_src)
    """

    def __init__(self, config: Dict[str, Any] = None):
        cfg = config or {}
        fc_cfg = cfg.get("forecasting", {})
        weights = fc_cfg.get("trend_score_weights", {})
        
        self.w_gt = weights.get("google_trends_momentum", 0.30)
        self.w_nlp = weights.get("nlp_keyword_prominence", 0.25)
        self.w_sem = weights.get("semantic_confidence", 0.20)
        self.w_sent = weights.get("sentiment_valence", 0.15)
        self.w_src = weights.get("source_diversity", 0.10)

        # Normalize weights to sum to 1.0
        total_w = self.w_gt + self.w_nlp + self.w_sem + self.w_sent + self.w_src
        if total_w > 0:
            self.w_gt /= total_w
            self.w_nlp /= total_w
            self.w_sem /= total_w
            self.w_sent /= total_w
            self.w_src /= total_w

    def classify_stage(self, score: float) -> str:
        """Categorizes score into standard fashion forecasting stages."""
        if score >= 75:
            return "Emerging"
        elif score >= 55:
            return "Growing"
        elif score >= 35:
            return "Stable"
        else:
            return "Declining"

    def compute_score(
        self,
        gt_momentum: float = 70.0,
        nlp_prominence: float = 65.0,
        semantic_confidence: float = 80.0,
        sentiment_valence: float = 60.0,
        source_count: int = 3
    ) -> Dict[str, Any]:
        """
        Calculates composite score, breakdown components, and trend stage.
        """
        # Clamp inputs to [0, 100]
        gt_norm = max(0.0, min(100.0, float(gt_momentum)))
        nlp_norm = max(0.0, min(100.0, float(nlp_prominence)))
        sem_norm = max(0.0, min(100.0, float(semantic_confidence)))
        sent_norm = max(0.0, min(100.0, float(sentiment_valence)))
        
        # Source diversity: 1 source=40, 2=70, 3=90, 4+=100
        src_norm = min(100.0, max(20.0, source_count * 30.0))

        weighted_gt = gt_norm * self.w_gt
        weighted_nlp = nlp_norm * self.w_nlp
        weighted_sem = sem_norm * self.w_sem
        weighted_sent = sent_norm * self.w_sent
        weighted_src = src_norm * self.w_src

        composite = weighted_gt + weighted_nlp + weighted_sem + weighted_sent + weighted_src
        composite = round(max(0.0, min(100.0, composite)), 1)

        stage = self.classify_stage(composite)

        return {
            "trend_score": composite,
            "trend_stage": stage,
            "breakdown": {
                "google_trends_momentum": {
                    "raw": gt_norm,
                    "weighted": round(weighted_gt, 2),
                    "weight_pct": round(self.w_gt * 100, 1)
                },
                "nlp_keyword_prominence": {
                    "raw": nlp_norm,
                    "weighted": round(weighted_nlp, 2),
                    "weight_pct": round(self.w_nlp * 100, 1)
                },
                "semantic_confidence": {
                    "raw": sem_norm,
                    "weighted": round(weighted_sem, 2),
                    "weight_pct": round(self.w_sem * 100, 1)
                },
                "sentiment_valence": {
                    "raw": sent_norm,
                    "weighted": round(weighted_sent, 2),
                    "weight_pct": round(self.w_sent * 100, 1)
                },
                "source_diversity": {
                    "raw": src_norm,
                    "weighted": round(weighted_src, 2),
                    "weight_pct": round(self.w_src * 100, 1)
                }
            }
        }
