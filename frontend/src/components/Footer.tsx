"use client";

import React from "react";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-top">
          <div className="footer-brand">
            <span className="footer-logo">The Indian Fashion Forecasting Lab</span>
            <p className="footer-description">
              Pioneering retail analytics, forecasting tomorrow&apos;s style through real-time search trends, culture, identity, and Google Gemini AI.
            </p>
          </div>

          <div className="footer-links-group">
            <div className="footer-links-col">
              <h4>Platform</h4>
              <a href="#forecaster" className="footer-link">Trend Forecaster</a>
              <a href="#moodboards" className="footer-link">Instagram Moodboards</a>
            </div>

            <div className="footer-links-col">
              <h4>Curation Sources</h4>
              <span className="footer-static-link">Google Trends</span>
              <span className="footer-static-link">Pinterest Live API</span>
              <span className="footer-static-link">Google Gemini API Key</span>
              <span className="footer-static-link">Unsplash Live Engine</span>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="copyright">
            &copy; {currentYear} The Indian Fashion Forecasting Lab. All rights reserved.
            Designed for professional Indian fashion houses, labels, and textile manufacturers.
          </p>
          <button
            type="button"
            className="back-to-top"
            onClick={scrollToTop}
            aria-label="Scroll to top"
          >
            ↑ Back to top
          </button>
        </div>
      </div>
    </footer>
  );
}
