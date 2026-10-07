"use client";

import React from "react";
import Link from "next/link";

export default function AboutSection() {
  return (
    <div id="about-project" className="box about-box">
      <div style={{ display: "inline-block", padding: "4px 12px", background: "rgba(139, 90, 43, 0.1)", borderRadius: "20px", color: "#8b5a2b", fontSize: "11px", fontWeight: 700, letterSpacing: "0.08em", marginBottom: "12px", textTransform: "uppercase" }}>
        NLP + LLM ARCHITECTURAL SPECIFICATION
      </div>
      <h2>About the Model</h2>
      <p className="about-intro">
        The Fashion Trend Intelligence &amp; Forecasting System is an academic Natural Language
        Processing and Large Language Model architecture developed to analyze fashion discourse, runway reports, and digital search
        signals for the Indian apparel market.
      </p>

      <div className="about-grid">
        <div className="about-card">
          <div className="card-header-icon">🔬</div>
          <h3>1. NLP Preprocessing &amp; Tokenization</h3>
          <p>
            Implements regex cleaning, punctuation normalization, customized fashion stopword filtering,
            and domain-specific lemmatization to extract content tokens, lexical diversity, and vocabulary distributions.
          </p>
        </div>

        <div className="about-card">
          <div className="card-header-icon">📊</div>
          <h3>2. TF-IDF &amp; Taxonomy Keyword Extraction</h3>
          <p>
            Extracts unigram and bigram key terms using Scikit-Learn TF-IDF vectorization boosted with domain-specific
            fashion taxonomy weights (garments, fabrics, aesthetics, and regional handloom terminology).
          </p>
        </div>

        <div className="about-card">
          <div className="card-header-icon">🏷️</div>
          <h3>3. Fashion Named Entity Recognition (NER)</h3>
          <p>
            Categorizes textual spans into 6 structured entity categories: Garments &amp; Silhouettes, Aesthetics,
            Fabrics &amp; Materials, Color Palettes, Indian Regional Crafts (e.g. Chikankari, Bandhani), and Demographics.
          </p>
        </div>

        <div className="about-card">
          <div className="card-header-icon">🧠</div>
          <h3>4. LLM Semantic Extraction &amp; Prompt System</h3>
          <p>
            Integrated with Google Gemini 2.5 Flash via dedicated externalized prompts (in <code>prompts/</code>) with
            strict Pydantic schema validation, anti-hallucination evidence grounding, and automatic JSON repair.
          </p>
        </div>

        <div className="about-card">
          <div className="card-header-icon">📈</div>
          <h3>5. Multi-Signal Trend Intelligence Scoring</h3>
          <p>
            Computes a transparent composite score (0–100) combining Google Trends momentum (30%), NLP keyword prominence (25%),
            semantic confidence (20%), contextual sentiment valence (15%), and source diversity (10%).
          </p>
        </div>

        <div className="about-card">
          <div className="card-header-icon">⚡</div>
          <h3>6. High-Efficiency Redis Caching Layer</h3>
          <p>
            Employs MD5-keyed 24-hour caching to minimize redundant LLM and search API calls, enabling high-speed
            in-memory retrieval on repeated inputs while tracking real measured execution latency.
          </p>
        </div>
      </div>

      <div style={{ textAlign: "center", margin: "30px 0 10px 0" }}>
        <Link
          href="/analyze"
          style={{
            display: "inline-block",
            padding: "12px 28px",
            background: "linear-gradient(135deg, #8b5a2b, #50352d)",
            color: "#ffffff",
            borderRadius: "8px",
            fontWeight: 700,
            textDecoration: "none",
            fontSize: "14px",
            boxShadow: "0 4px 14px rgba(80, 53, 45, 0.2)"
          }}
        >
          Launch NLP Trend Analyzer
        </Link>
      </div>

      <div className="about-stats-panel" style={{ marginTop: "24px" }}>
        <div className="stat-item">
          <span className="stat-number">6-Stage</span>
          <span className="stat-label">NLP &amp; LLM Pipeline</span>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <span className="stat-number">0–100</span>
          <span className="stat-label">Explainable Trend Score</span>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <span className="stat-number">Pydantic</span>
          <span className="stat-label">Verified JSON Schemas</span>
        </div>
        <div className="stat-divider"></div>
        <div className="stat-item">
          <span className="stat-number">Real-Time</span>
          <span className="stat-label">Measured Execution Profiling</span>
        </div>
      </div>
    </div>
  );
}
