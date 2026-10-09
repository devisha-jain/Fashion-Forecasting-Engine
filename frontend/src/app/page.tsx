"use client";

import { useState } from "react";
import TrendCard, { Trend } from "@/components/TrendCard";
import MoodboardSection from "@/components/MoodboardSection";
import Lightbox from "@/components/Lightbox";
import Fuse from "fuse.js";
import { FASHION_KEYWORDS } from "@/components/keywords";
import Navbar from "@/components/Navbar";
import AboutSection from "@/components/AboutSection";
import Footer from "@/components/Footer";
import { getApiUrl } from "@/lib/api";

export default function Home() {
  const [region, setRegion] = useState("Pan India");
  const [year, setYear] = useState("2026");
  const [signals, setSignals] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [cached, setCached] = useState(false);
  const [forecasts, setForecasts] = useState<Trend[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Autocomplete search states
  const [inputValue, setInputValue] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  // Lightbox state
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxTitle, setLightboxTitle] = useState("");
  const [lightboxImages, setLightboxImages] = useState<string[]>([]);
  const [lightboxIndex, setLightboxIndex] = useState(0);

  const openLightbox = (title: string, images: string[]) => {
    setLightboxTitle(title);
    setLightboxImages(images);
    setLightboxIndex(0);
    setLightboxOpen(true);
  };

  // Initialize Fuse.js for fuzzy autocomplete
  const fuse = new Fuse(FASHION_KEYWORDS, {
    threshold: 0.4,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setInputValue(val);
    if (val.trim()) {
      const results = fuse.search(val).map((r) => r.item);
      setSuggestions(results);
      setShowDropdown(true);
    } else {
      setSuggestions([]);
      setShowDropdown(false);
    }
  };

  const addTag = (tag: string) => {
    const cleanTag = tag.trim().toLowerCase();
    if (!cleanTag) return;

    // Try to find exact case match in keywords list for consistent formatting
    const match = FASHION_KEYWORDS.find((k) => k.toLowerCase() === cleanTag);
    const tagToAdd = match || tag.trim();

    if (!signals.includes(tagToAdd)) {
      setSignals([...signals, tagToAdd]);
    }
    setInputValue("");
    setSuggestions([]);
    setShowDropdown(false);
  };

  const removeTag = (tagToRemove: string) => {
    setSignals(signals.filter((tag) => tag !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const activeSignals = [...signals];

    // Automatically add whatever is left in the text box if not empty
    if (inputValue.trim()) {
      const cleanTag = inputValue.trim().toLowerCase();
      const match = FASHION_KEYWORDS.find((k) => k.toLowerCase() === cleanTag);
      const tagToAdd = match || inputValue.trim();
      if (!activeSignals.includes(tagToAdd)) {
        activeSignals.push(tagToAdd);
        setSignals(activeSignals);
      }
      setInputValue("");
      setSuggestions([]);
      setShowDropdown(false);
    }

    if (activeSignals.length === 0) return;

    setLoading(true);
    setError(null);
    try {
      // Pass the exact/latest search term as a URL query parameter for integration pattern
      const latestTerm = activeSignals[activeSignals.length - 1];
      const url = `/api/forecast?signal=${encodeURIComponent(latestTerm)}`;

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ region, year, signals: activeSignals }),
      });
      if (!res.ok) {
        let errorMsg = `Server error (${res.status})`;
        try {
          const errData = await res.json();
          errorMsg = errData.error || errData.details || errorMsg;
        } catch {
          try {
            const rawText = await res.text();
            if (rawText) errorMsg = rawText.slice(0, 200);
          } catch { }
        }
        throw new Error(errorMsg);
      }
      const data = await res.json();
      setForecasts(data.forecasts || []);
      setCached(data.cached || false);
    } catch (err: any) {
      console.error("Forecast error:", err);
      const isConnectionRefused = err?.message === "Failed to fetch" || err?.name === "TypeError";
      setError(
        isConnectionRefused
          ? "Unable to reach the backend forecasting API (/api/forecast). Please ensure the backend service is deployed and active."
          : err.message || "Failed to fetch forecasts."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <div className="container">
        {/* Hero */}
        <div id="hero" className="hero box hero-box">
          <h1>The Indian Fashion Forecasting Lab</h1>
          <p className="subtitle">
            Forecasting tomorrow&apos;s Indian style through culture, identity &amp;
            digital trends
          </p>
        </div>

        {/* Form */}
        <div id="forecaster" className="box form-box">
          <form onSubmit={handleSubmit}>
            <h2>Forecast Settings</h2>

            <div className="form-grid">
              <div className="input-group">
                <label>Region</label>
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                >
                  <option>Pan India</option>
                  <option>North India</option>
                  <option>South India</option>
                  <option>Metro Cities</option>
                </select>
              </div>

              <div className="input-group">
                <label>Forecast Year</label>
                <select
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                >
                  <option>2026</option>
                  <option>2027</option>
                  <option>2028</option>
                </select>
              </div>
            </div>

            <h2>Trend Signals</h2>

            {/* Tag container for active selections */}
            {signals.length > 0 && (
              <div className="tag-container">
                {signals.map((tag) => (
                  <div key={tag} className="tag-pill">
                    {tag}
                    <button
                      type="button"
                      className="tag-remove"
                      onClick={() => removeTag(tag)}
                      aria-label={`Remove ${tag}`}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Fuzzy Autocomplete Input Container */}
            <div className="autocomplete-container">
              <div className="autocomplete-input-wrapper">
                <input
                  type="text"
                  className="text-input"
                  placeholder="Search 70+ aesthetics (e.g. saree, cottagecore, y2k — press Enter to add)..."
                  value={inputValue}
                  onChange={handleInputChange}
                  onFocus={() => {
                    if (inputValue.trim()) setShowDropdown(true);
                  }}
                  onBlur={() => {
                    // Small timeout to let clicks register on the dropdown suggestions before hiding it
                    setTimeout(() => setShowDropdown(false), 200);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      if (inputValue.trim()) {
                        addTag(inputValue);
                      }
                    }
                  }}
                />
              </div>

              {/* Suggestions Dropdown */}
              {showDropdown && (
                <div className="autocomplete-dropdown">
                  {suggestions.length > 0 ? (
                    suggestions.map((suggestion) => (
                      <div
                        key={suggestion}
                        className="autocomplete-item"
                        onMouseDown={() => addTag(suggestion)}
                      >
                        {suggestion}
                      </div>
                    ))
                  ) : (
                    <div className="autocomplete-no-results">
                      No matching keywords found. Press Enter to use anyway!
                    </div>
                  )}
                </div>
              )}
            </div>
            <p className="small-text">
              Select keywords from suggestions, or type free-form and press Enter to add!
            </p>

            <button type="submit" disabled={loading || (signals.length === 0 && !inputValue.trim())}>
              {loading ? "Generating..." : "Generate Forecast"}
            </button>
          </form>
        </div>

        {/* Error State */}
        {error && (
          <div className="box" style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "12px", padding: "16px 20px", color: "#991b1b", marginBottom: "20px", fontSize: "14px" }}>
            <strong>⚠️ Request Error:</strong> {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="box">
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p className="loading-text">
                Analyzing Google Trends &amp; generating AI forecast...
              </p>
            </div>
          </div>
        )}

        {/* Forecast Results */}
        {!loading &&
          forecasts.map((trend, index) => (
            <TrendCard
              key={index}
              trend={trend}
              index={index}
              cached={cached}
            />
          ))}

        {/* Static Moodboard Section */}
        <div id="moodboards">
          <MoodboardSection openLightbox={openLightbox} />
        </div>

        {/* About Section */}
        <AboutSection />
      </div>

      {/* Footer */}
      <Footer />

      {/* Lightbox */}
      <Lightbox
        isOpen={lightboxOpen}
        title={lightboxTitle}
        images={lightboxImages}
        currentIndex={lightboxIndex}
        setCurrentIndex={setLightboxIndex}
        onClose={() => setLightboxOpen(false)}
      />
    </>
  );
}
