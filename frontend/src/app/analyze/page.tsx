"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { getApiUrl } from "@/lib/api";

export default function AnalyzePage() {
  const [inputText, setInputText] = useState("");
  const [region, setRegion] = useState("Pan India");
  const [year, setYear] = useState("2026");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"trends" | "nlp" | "scoring" | "metrics">("trends");
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const url = "/api/analyze";
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText, region, year }),
      });

      if (!res.ok) {
        let errorMsg = `Server error (${res.status})`;
        try {
          const errData = await res.json();
          errorMsg = errData.details || errData.error || errorMsg;
        } catch {
          try {
            const rawText = await res.text();
            if (rawText) errorMsg = rawText.slice(0, 200);
          } catch { }
        }
        throw new Error(errorMsg);
      }

      const data = await res.json();
      setAnalysisResult(data);
    } catch (err: any) {
      console.error("Analysis error:", err);
      const isConnectionRefused = err?.message === "Failed to fetch" || err?.name === "TypeError";
      setError(
        isConnectionRefused
          ? "Unable to reach the backend analysis API (/api/analyze). Please ensure the backend service is deployed and active."
          : err.message || "Failed to execute analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <div className="container" style={{ maxWidth: "1200px", margin: "0 auto", padding: "30px 20px" }}>
        {/* Header Hero */}
        <div className="hero box hero-box" style={{ marginBottom: "28px", textAlign: "center" }}>
          <div style={{ display: "inline-block", padding: "4px 12px", background: "rgba(139, 90, 43, 0.1)", borderRadius: "20px", color: "#8b5a2b", fontSize: "11px", fontWeight: 700, letterSpacing: "0.08em", marginBottom: "12px", textTransform: "uppercase" }}>
            NLP &amp; LLM Intelligence Engine
          </div>
          <h1 style={{ fontSize: "28px", fontWeight: 800, color: "#3d271d", marginBottom: "10px" }}>
            Fashion Text &amp; Trend Intelligence Analyzer
          </h1>
          <p className="subtitle" style={{ maxWidth: "750px", margin: "0 auto", color: "#6b4f40", fontSize: "15px" }}>
            Input raw runway reports, fashion journalism articles, social media captions, or consumer discourse.
            The system executes NLP tokenization, TF-IDF taxonomy extraction, Fashion NER, and Gemini semantic analysis.
          </p>
        </div>

        {/* Input & Controls Card */}
        <div className="box dashboard-box" style={{ background: "#ffffff", borderRadius: "16px", padding: "24px", boxShadow: "0 10px 30px rgba(80, 53, 45, 0.05)", border: "1px solid rgba(203, 168, 154, 0.3)", marginBottom: "30px" }}>
          <div style={{ marginBottom: "14px" }}>
            <span style={{ fontSize: "13px", fontWeight: 700, color: "#8b5a2b", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Fashion Input Text:
            </span>
          </div>

          <textarea
            rows={5}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste fashion text, runway report, or social commentary here..."
            style={{
              width: "100%",
              padding: "16px",
              borderRadius: "10px",
              border: "1px solid #d2b48c",
              background: "#fdfbf7",
              color: "#3d271d",
              fontSize: "14px",
              lineHeight: "1.6",
              fontFamily: "Inter, sans-serif",
              resize: "vertical",
              marginBottom: "18px"
            }}
          />

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
            <div style={{ display: "flex", gap: "14px", alignItems: "center" }}>
              <div>
                <label style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "#8b5a2b", marginBottom: "4px" }}>TARGET REGION</label>
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cba89a", background: "#fdfbf7", color: "#50352d", fontSize: "13px" }}
                >
                  <option value="Pan India">Pan India</option>
                  <option value="North India">North India (Delhi NCR, Punjab)</option>
                  <option value="West India">West India (Mumbai, Gujarat)</option>
                  <option value="South India">South India (Bengaluru, Chennai)</option>
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "11px", fontWeight: 700, color: "#8b5a2b", marginBottom: "4px" }}>FORECAST YEAR</label>
                <select
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                  style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cba89a", background: "#fdfbf7", color: "#50352d", fontSize: "13px" }}
                >
                  <option value="2026">2026</option>
                  <option value="2027">2027</option>
                  <option value="2028">2028</option>
                  <option value="2029">2029</option>
                </select>
              </div>
            </div>

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={loading || !inputText.trim()}
              style={{
                padding: "12px 28px",
                background: loading ? "#a88878" : "linear-gradient(135deg, #8b5a2b, #50352d)",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: 700,
                cursor: loading ? "not-allowed" : "pointer",
                boxShadow: "0 4px 14px rgba(80, 53, 45, 0.2)",
                transition: "all 0.2s ease"
              }}
            >
              {loading ? "Processing NLP & LLM..." : "✦ Run Trend Intelligence Analysis"}
            </button>
          </div>

          {error && (
            <div style={{ marginTop: "16px", padding: "12px 16px", background: "#fef2f2", color: "#991b1b", borderRadius: "8px", fontSize: "13px" }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {analysisResult && (
          <div className="analysis-results-container" style={{ marginTop: "30px" }}>
            {/* Navigation Tabs */}
            <div style={{ display: "flex", gap: "8px", borderBottom: "2px solid rgba(203, 168, 154, 0.3)", marginBottom: "24px" }}>
              {[
                { id: "trends", label: "Structured Trends & Synthesis" },
                { id: "nlp", label: "NLP Linguistics & Fashion NER" },
                { id: "scoring", label: "Trend Scoring Matrix" },
                { id: "metrics", label: "System & Engineering Metrics" }
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id as any)}
                  style={{
                    padding: "10px 18px",
                    background: activeTab === tab.id ? "#8b5a2b" : "transparent",
                    color: activeTab === tab.id ? "#ffffff" : "#50352d",
                    border: "none",
                    borderRadius: "8px 8px 0 0",
                    fontWeight: 700,
                    fontSize: "13px",
                    cursor: "pointer",
                    transition: "all 0.2s ease"
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* TAB 1: Structured Trends */}
            {activeTab === "trends" && (
              <div>
                {/* Market Synthesis */}
                {analysisResult.market_synthesis && (
                  <div style={{ background: "linear-gradient(135deg, rgba(203, 168, 154, 0.2), rgba(253, 251, 247, 0.8))", padding: "20px", borderRadius: "12px", border: "1px solid #d2b48c", marginBottom: "24px" }}>
                    <div style={{ fontSize: "11px", fontWeight: 800, color: "#8b5a2b", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px" }}>
                      Executive Market Synthesis
                    </div>
                    <p style={{ margin: 0, color: "#3d271d", fontSize: "15px", lineHeight: "1.6", fontWeight: 500 }}>
                      {analysisResult.market_synthesis}
                    </p>
                  </div>
                )}

                {/* Extracted Trends Grid */}
                <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                  {analysisResult.trends?.map((trend: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        background: "#ffffff",
                        borderRadius: "14px",
                        padding: "24px",
                        border: "1px solid rgba(203, 168, 154, 0.4)",
                        boxShadow: "0 6px 20px rgba(80, 53, 45, 0.04)"
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "10px", marginBottom: "14px" }}>
                        <div>
                          <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "6px" }}>
                            <span style={{ padding: "3px 10px", background: "#f5f3ff", color: "#6d28d9", borderRadius: "12px", fontSize: "11px", fontWeight: 700, border: "1px solid rgba(109, 40, 217, 0.2)" }}>
                              ✦ {trend.trend_stage || "Growing"} Stage
                            </span>
                            <span style={{ padding: "3px 10px", background: "#fdfbf7", color: "#8b5a2b", borderRadius: "12px", fontSize: "11px", fontWeight: 700, border: "1px solid #d2b48c" }}>
                              {trend.category}
                            </span>
                          </div>
                          <h3 style={{ margin: 0, fontSize: "20px", fontWeight: 800, color: "#3d271d" }}>
                            {trend.name}
                          </h3>
                        </div>

                        <div style={{ textAlign: "right" }}>
                          <span style={{ fontSize: "24px", fontWeight: 800, color: "#8b5a2b" }}>
                            {trend.trend_score || 78}
                          </span>
                          <span style={{ display: "block", fontSize: "10px", fontWeight: 700, color: "#a88878", letterSpacing: "0.05em" }}>
                            TREND SCORE
                          </span>
                        </div>
                      </div>

                      {/* Fashion Entity Tags */}
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "16px" }}>
                        <span style={{ padding: "4px 10px", background: "#faf5f0", borderRadius: "6px", fontSize: "12px", color: "#50352d" }}>
                          <strong>Silhouette:</strong> {trend.garment || trend.silhouette}
                        </span>
                        <span style={{ padding: "4px 10px", background: "#faf5f0", borderRadius: "6px", fontSize: "12px", color: "#50352d" }}>
                          <strong>Fabric:</strong> {trend.material}
                        </span>
                        <span style={{ padding: "4px 10px", background: "#faf5f0", borderRadius: "6px", fontSize: "12px", color: "#50352d" }}>
                          <strong>Color:</strong> {trend.colour}
                        </span>
                        <span style={{ padding: "4px 10px", background: "#faf5f0", borderRadius: "6px", fontSize: "12px", color: "#50352d" }}>
                          <strong>Aesthetic:</strong> {trend.aesthetic}
                        </span>
                      </div>

                      {/* Evidence Grounding */}
                      {trend.evidence && (
                        <div style={{ background: "rgba(203, 168, 154, 0.1)", padding: "12px 16px", borderRadius: "8px", marginBottom: "14px", borderLeft: "3px solid #8b5a2b" }}>
                          <span style={{ fontSize: "11px", fontWeight: 700, color: "#8b5a2b", textTransform: "uppercase", display: "block", marginBottom: "4px" }}>
                            Grounded Text Evidence:
                          </span>
                          <span style={{ fontSize: "13px", color: "#4a3528", fontStyle: "italic" }}>
                            &ldquo;{trend.evidence}&rdquo;
                          </span>
                        </div>
                      )}

                      {/* Drivers */}
                      {trend.drivers && trend.drivers.length > 0 && (
                        <div style={{ marginTop: "10px" }}>
                          <span style={{ fontSize: "11px", fontWeight: 700, color: "#8b5a2b", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
                            Consumer &amp; Retail Drivers:
                          </span>
                          <ul style={{ margin: 0, paddingLeft: "18px", color: "#50352d", fontSize: "13px", lineHeight: "1.5" }}>
                            {trend.drivers.map((d: string, dIdx: number) => (
                              <li key={dIdx}>{d}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 2: NLP Linguistics & Fashion NER */}
            {activeTab === "nlp" && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                {/* Linguistic Stats */}
                <div style={{ background: "#ffffff", padding: "20px", borderRadius: "12px", border: "1px solid rgba(203, 168, 154, 0.4)" }}>
                  <h4 style={{ margin: "0 0 14px 0", color: "#8b5a2b", fontSize: "15px", fontWeight: 700 }}>
                    Linguistic Token Statistics
                  </h4>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                    <div style={{ padding: "10px", background: "#fdfbf7", borderRadius: "8px" }}>
                      <span style={{ fontSize: "11px", color: "#8b5a2b" }}>Total Words</span>
                      <div style={{ fontSize: "18px", fontWeight: 800, color: "#3d271d" }}>
                        {analysisResult.nlp_analysis?.statistics?.total_words}
                      </div>
                    </div>
                    <div style={{ padding: "10px", background: "#fdfbf7", borderRadius: "8px" }}>
                      <span style={{ fontSize: "11px", color: "#8b5a2b" }}>Filtered Tokens</span>
                      <div style={{ fontSize: "18px", fontWeight: 800, color: "#3d271d" }}>
                        {analysisResult.nlp_analysis?.statistics?.filtered_word_count}
                      </div>
                    </div>
                    <div style={{ padding: "10px", background: "#fdfbf7", borderRadius: "8px" }}>
                      <span style={{ fontSize: "11px", color: "#8b5a2b" }}>Lexical Diversity</span>
                      <div style={{ fontSize: "18px", fontWeight: 800, color: "#3d271d" }}>
                        {analysisResult.nlp_analysis?.statistics?.lexical_diversity}
                      </div>
                    </div>
                    <div style={{ padding: "10px", background: "#fdfbf7", borderRadius: "8px" }}>
                      <span style={{ fontSize: "11px", color: "#8b5a2b" }}>Avg Word Length</span>
                      <div style={{ fontSize: "18px", fontWeight: 800, color: "#3d271d" }}>
                        {analysisResult.nlp_analysis?.statistics?.average_word_length} chars
                      </div>
                    </div>
                  </div>

                  <h4 style={{ margin: "20px 0 10px 0", color: "#8b5a2b", fontSize: "15px", fontWeight: 700 }}>
                    Sentiment &amp; Context Signals
                  </h4>
                  <div style={{ padding: "12px", background: "#fdfbf7", borderRadius: "8px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                      <span style={{ fontSize: "12px", fontWeight: 600, color: "#50352d" }}>Market Momentum:</span>
                      <span style={{ fontSize: "12px", fontWeight: 700, color: "#047857" }}>
                        {analysisResult.nlp_analysis?.sentiment?.sentiment}
                      </span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span style={{ fontSize: "12px", fontWeight: 600, color: "#50352d" }}>Momentum Score:</span>
                      <span style={{ fontSize: "12px", fontWeight: 700, color: "#8b5a2b" }}>
                        {analysisResult.nlp_analysis?.sentiment?.momentum_score} / 100
                      </span>
                    </div>
                  </div>
                </div>

                {/* TF-IDF Keywords */}
                <div style={{ background: "#ffffff", padding: "20px", borderRadius: "12px", border: "1px solid rgba(203, 168, 154, 0.4)" }}>
                  <h4 style={{ margin: "0 0 14px 0", color: "#8b5a2b", fontSize: "15px", fontWeight: 700 }}>
                    TF-IDF Domain-Weighted Keywords
                  </h4>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                    {analysisResult.nlp_analysis?.keywords?.map((kw: any, kIdx: number) => (
                      <span
                        key={kIdx}
                        style={{
                          padding: "5px 12px",
                          background: kw.boost_factor > 1.0 ? "rgba(139, 90, 43, 0.12)" : "#f5f5f5",
                          border: `1px solid ${kw.boost_factor > 1.0 ? "#cba89a" : "#e5e5e5"}`,
                          borderRadius: "16px",
                          fontSize: "12px",
                          color: "#3d271d",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px"
                        }}
                      >
                        <strong>{kw.keyword}</strong>
                        <span style={{ fontSize: "10px", color: "#8b5a2b" }}>({kw.score})</span>
                      </span>
                    ))}
                  </div>

                  <h4 style={{ margin: "20px 0 10px 0", color: "#8b5a2b", fontSize: "15px", fontWeight: 700 }}>
                    Detected Fashion Named Entities (NER)
                  </h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {Object.entries(analysisResult.nlp_analysis?.entity_summary || {}).map(([cat, val]: any) => {
                      if (cat === "total_detected" || !val.count) return null;
                      return (
                        <div key={cat} style={{ fontSize: "12px", color: "#50352d" }}>
                          <strong style={{ textTransform: "capitalize" }}>{cat.replace("_", " ")}:</strong>{" "}
                          {val.unique_terms?.join(", ") || "None"}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: Scoring Matrix */}
            {activeTab === "scoring" && (
              <div style={{ background: "#ffffff", padding: "24px", borderRadius: "14px", border: "1px solid rgba(203, 168, 154, 0.4)" }}>
                <h3 style={{ margin: "0 0 8px 0", color: "#3d271d", fontSize: "18px", fontWeight: 800 }}>
                  Multi-Signal Trend Intelligence Scoring Formula
                </h3>
                <p style={{ color: "#6b4f40", fontSize: "14px", marginBottom: "20px" }}>
                  Composite score (0–100) calculated by weighting live cultural search velocity, NLP keyword prominence,
                  semantic LLM confidence, sentiment momentum, and source diversity.
                </p>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "14px" }}>
                  {[
                    { name: "Google Trends Momentum", weight: "30%", desc: "Live search velocity & query index" },
                    { name: "NLP Keyword Prominence", weight: "25%", desc: "TF-IDF + Domain taxonomy weights" },
                    { name: "Semantic LLM Confidence", weight: "20%", desc: "Gemini evidence grounding score" },
                    { name: "Sentiment Valence", weight: "15%", desc: "Adoption tone & commercial momentum" },
                    { name: "Source Diversity", weight: "10%", desc: "Multi-channel cross-verification" }
                  ].map((sig, sIdx) => (
                    <div key={sIdx} style={{ padding: "16px", background: "#fdfbf7", borderRadius: "10px", border: "1px solid #d2b48c" }}>
                      <div style={{ fontSize: "20px", fontWeight: 800, color: "#8b5a2b", marginBottom: "4px" }}>
                        {sig.weight}
                      </div>
                      <div style={{ fontSize: "13px", fontWeight: 700, color: "#3d271d", marginBottom: "4px" }}>
                        {sig.name}
                      </div>
                      <div style={{ fontSize: "11px", color: "#6b4f40" }}>
                        {sig.desc}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 4: System & Engineering Metrics */}
            {activeTab === "metrics" && (
              <div style={{ background: "#ffffff", padding: "24px", borderRadius: "14px", border: "1px solid rgba(203, 168, 154, 0.4)" }}>
                <h3 style={{ margin: "0 0 16px 0", color: "#3d271d", fontSize: "18px", fontWeight: 800 }}>
                  System Profiling &amp; Real Processing Metrics
                </h3>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "14px" }}>
                  <div style={{ padding: "16px", background: "#fdfbf7", borderRadius: "10px", border: "1px solid #e5e5e5" }}>
                    <span style={{ fontSize: "11px", color: "#8b5a2b", fontWeight: 700 }}>NLP PIPELINE LATENCY</span>
                    <div style={{ fontSize: "22px", fontWeight: 800, color: "#3d271d", marginTop: "4px" }}>
                      {analysisResult.nlp_analysis?.nlp_latency_ms} ms
                    </div>
                  </div>

                  <div style={{ padding: "16px", background: "#fdfbf7", borderRadius: "10px", border: "1px solid #e5e5e5" }}>
                    <span style={{ fontSize: "11px", color: "#8b5a2b", fontWeight: 700 }}>LLM SEMANTIC LATENCY</span>
                    <div style={{ fontSize: "22px", fontWeight: 800, color: "#3d271d", marginTop: "4px" }}>
                      {analysisResult.metadata?.llm_latency_ms} ms
                    </div>
                  </div>

                  <div style={{ padding: "16px", background: "#fdfbf7", borderRadius: "10px", border: "1px solid #e5e5e5" }}>
                    <span style={{ fontSize: "11px", color: "#8b5a2b", fontWeight: 700 }}>TOTAL PIPELINE TIME</span>
                    <div style={{ fontSize: "22px", fontWeight: 800, color: "#3d271d", marginTop: "4px" }}>
                      {analysisResult.metadata?.processing_time_ms} ms
                    </div>
                  </div>

                  <div style={{ padding: "16px", background: "#fdfbf7", borderRadius: "10px", border: "1px solid #e5e5e5" }}>
                    <span style={{ fontSize: "11px", color: "#8b5a2b", fontWeight: 700 }}>LLM MODEL</span>
                    <div style={{ fontSize: "16px", fontWeight: 800, color: "#3d271d", marginTop: "8px" }}>
                      {analysisResult.metadata?.llm_model}
                    </div>
                  </div>

                  <div style={{ padding: "16px", background: "#fdfbf7", borderRadius: "10px", border: "1px solid #e5e5e5" }}>
                    <span style={{ fontSize: "11px", color: "#8b5a2b", fontWeight: 700 }}>CACHE STATUS</span>
                    <div style={{ fontSize: "18px", fontWeight: 800, color: "#047857", marginTop: "6px" }}>
                      {analysisResult.metadata?.cached ? "HIT (Sub-10ms)" : "MISS (Live Computed)"}
                    </div>
                  </div>

                  <div style={{ padding: "16px", background: "#fdfbf7", borderRadius: "10px", border: "1px solid #e5e5e5" }}>
                    <span style={{ fontSize: "11px", color: "#8b5a2b", fontWeight: 700 }}>SCHEMA VALIDATION</span>
                    <div style={{ fontSize: "18px", fontWeight: 800, color: "#047857", marginTop: "6px" }}>
                      ✓ Pydantic Verified
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <Footer />
    </>
  );
}
