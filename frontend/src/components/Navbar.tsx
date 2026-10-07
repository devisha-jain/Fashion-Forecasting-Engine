"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  const handleNavClick = (id: string) => {
    if (pathname === "/") {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
    } else {
      router.push(`/#${id}`);
    }
    setIsOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link href="/" className="navbar-logo" style={{ textDecoration: "none" }}>
          The Indian Fashion Forecasting Lab
        </Link>

        {/* Desktop Links */}
        <div className="navbar-links desktop-only" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <button
            type="button"
            className={`nav-link ${pathname === "/" ? "active" : ""}`}
            onClick={() => handleNavClick("forecaster")}
          >
            Forecaster
          </button>
          <Link
            href="/analyze"
            className={`nav-link ${pathname === "/analyze" ? "active" : ""}`}
            style={{
              textDecoration: "none",
              background: pathname === "/analyze" ? "rgba(139, 90, 43, 0.15)" : "rgba(203, 168, 154, 0.2)",
              padding: "6px 14px",
              borderRadius: "20px",
              fontWeight: 700,
              color: "#8b5a2b",
              border: "1px solid rgba(203, 168, 154, 0.5)"
            }}
          >
            Trend Analyzer using NLP
          </Link>
          <button
            type="button"
            className="nav-link"
            onClick={() => handleNavClick("moodboards")}
          >
            Instagram Trends
          </button>
          <button
            type="button"
            className="nav-link nav-link-about"
            onClick={() => handleNavClick("about-project")}
          >
            About the Model
          </button>
        </div>

        {/* Hamburger Icon */}
        <button
          type="button"
          className={`hamburger-menu ${isOpen ? "open" : ""}`}
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation menu"
        >
          <span className="bar"></span>
          <span className="bar"></span>
          <span className="bar"></span>
        </button>
      </div>

      {/* Mobile Links Dropdown */}
      <div className={`mobile-nav-menu ${isOpen ? "open" : ""}`}>
        <button
          type="button"
          className="mobile-nav-link"
          onClick={() => handleNavClick("forecaster")}
        >
          Forecaster
        </button>
        <Link
          href="/analyze"
          className="mobile-nav-link"
          style={{ textDecoration: "none", color: "#8b5a2b", fontWeight: 700 }}
          onClick={() => setIsOpen(false)}
        >
          NLP Trend Analyzer
        </Link>
        <button
          type="button"
          className="mobile-nav-link"
          onClick={() => handleNavClick("moodboards")}
        >
          Instagram Trends
        </button>
        <button
          type="button"
          className="mobile-nav-link"
          onClick={() => handleNavClick("about-project")}
        >
          About the Model
        </button>
      </div>
    </nav>
  );
}
