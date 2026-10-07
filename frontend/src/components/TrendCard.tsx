"use client";

import { useEffect, useRef, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  LineController,
  PointElement,
  BarElement,
  BarController,
  ArcElement,
  DoughnutController,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  LineController,
  PointElement,
  BarElement,
  BarController,
  ArcElement,
  DoughnutController,
  Filler,
  Tooltip,
  Legend
);

const CHART_COLORS = [
  "#cba89a", // baby pink/nude
  "#8b5a2b", // rich brown
  "#d2b48c", // beige
  "#50352d"  // dark brown
];

export interface Trend {
  name: string;
  confidence?: number;
  trend_score?: number;
  trend_stage?: string;
  description: string;
  business?: string;
  strategic_advice?: string;
  momentum?: string;
  palette?: string[];
  graph?: Record<string, number>;
  demographics?: Record<string, number>;
  image?: string;
  images?: string[];
  sources?: string[];
  yearlyForecast?: Array<{ year: string; score: number }>;
  risks?: string;
  targetDemographic?: string;
  peakSeason?: string;
  competitorActivity?: string;
  consumer_drivers?: string[];
  garment?: string;
  material?: string;
  colour?: string;
  aesthetic?: string;
  category?: string;
  evidence?: string;
  score_breakdown?: any;
}

interface TrendCardProps {
  trend: Trend;
  index: number;
  cached: boolean;
}

const STAGE_CONFIG: Record<string, { label: string; color: string; bg: string; border: string }> = {
  Emerging: {
    label: "Emerging Trend",
    color: "#6d28d9",
    bg: "#f5f3ff",
    border: "rgba(109, 40, 217, 0.3)",
  },
  Growing: {
    label: "Growing Momentum",
    color: "#047857",
    bg: "#ecfdf5",
    border: "rgba(4, 120, 87, 0.3)",
  },
  Stable: {
    label: "Stable Demand",
    color: "#b45309",
    bg: "#fffbeb",
    border: "rgba(180, 83, 9, 0.3)",
  },
  Declining: {
    label: "Saturating / Declining",
    color: "#b91c1c",
    bg: "#fef2f2",
    border: "rgba(185, 28, 28, 0.3)",
  },
};

export default function TrendCard({ trend, index, cached }: TrendCardProps) {
  const lineRef = useRef<HTMLCanvasElement>(null);
  const lineChartRef = useRef<ChartJS | null>(null);

  const barRef = useRef<HTMLCanvasElement>(null);
  const barChartRef = useRef<ChartJS | null>(null);

  const pieRef = useRef<HTMLCanvasElement>(null);
  const pieChartRef = useRef<ChartJS | null>(null);

  const [imagesLoaded, setImagesLoaded] = useState<boolean[]>([false, false, false]);
  const [lightboxSrc, setLightboxSrc] = useState<string | null>(null);

  const getStageConfig = (stage: string | undefined) => {
    const s = stage?.trim() || "Growing";
    if (s.includes("Emerg")) return STAGE_CONFIG["Emerging"];
    if (s.includes("Grow")) return STAGE_CONFIG["Growing"];
    if (s.includes("Stab")) return STAGE_CONFIG["Stable"];
    if (s.includes("Declin")) return STAGE_CONFIG["Declining"];
    return STAGE_CONFIG["Growing"];
  };

  const stageConfig = getStageConfig(trend.trend_stage);
  const displayScore = trend.trend_score ?? (trend.confidence ? Math.round(trend.confidence > 1 ? trend.confidence : trend.confidence * 100) : 78);

  // Yearly projection line chart
  useEffect(() => {
    if (!lineRef.current || !trend.yearlyForecast?.length) return;
    if (lineChartRef.current) lineChartRef.current.destroy();
    const ctx = lineRef.current.getContext("2d");
    if (!ctx) return;

    const gradient = ctx.createLinearGradient(0, 0, 0, 160);
    gradient.addColorStop(0, "rgba(203, 168, 154, 0.25)");
    gradient.addColorStop(1, "rgba(203, 168, 154, 0.01)");

    const datalabelsPlugin = {
      id: "datalabels",
      afterDatasetsDraw(chart: ChartJS) {
        const { ctx, data } = chart;
        ctx.save();
        ctx.font = "bold 11px Inter, sans-serif";
        ctx.fillStyle = "#8b5a2b";
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";

        chart.getDatasetMeta(0).data.forEach((point: unknown, idx: number) => {
          const p = point as { x: number; y: number };
          const value = data.datasets[0].data[idx];
          if (value !== undefined && value !== null) {
            ctx.fillText(value.toString(), p.x, p.y - 8);
          }
        });
        ctx.restore();
      }
    };

    lineChartRef.current = new ChartJS(ctx, {
      type: "line",
      data: {
        labels: trend.yearlyForecast.map((d) => d.year),
        datasets: [
          {
            label: "Adoption Index",
            data: trend.yearlyForecast.map((d) => d.score),
            borderColor: "#cba89a",
            backgroundColor: gradient,
            borderWidth: 2,
            pointBackgroundColor: "#8b5a2b",
            pointBorderColor: "#ffffff",
            pointBorderWidth: 1.5,
            pointRadius: 5.5,
            pointHoverRadius: 7,
            tension: 0.2,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            top: 20,
            bottom: 5,
            left: 10,
            right: 10
          }
        },
        scales: {
          y: {
            display: false,
            beginAtZero: false,
            min: 0,
            max: 110
          },
          x: {
            grid: { display: false },
            ticks: {
              color: "#8b5a2b",
              font: {
                family: "Inter",
                size: 11,
                weight: "normal"
              }
            },
            border: { display: false }
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true }
        },
      },
      plugins: [datalabelsPlugin]
    });

    return () => {
      if (lineChartRef.current) lineChartRef.current.destroy();
    };
  }, [trend.yearlyForecast]);

  // Bar Chart (Signal Strength)
  useEffect(() => {
    if (!barRef.current || !trend.graph) return;
    if (barChartRef.current) barChartRef.current.destroy();
    const ctx = barRef.current.getContext("2d");
    if (!ctx) return;

    const labels = Object.keys(trend.graph);
    const dataValues = Object.values(trend.graph);

    barChartRef.current = new ChartJS(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Signal Strength",
            data: dataValues,
            backgroundColor: CHART_COLORS,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: {
              color: "rgba(139, 90, 43, 0.05)",
            },
            ticks: {
              color: "#8b5a2b",
              font: {
                family: "Inter",
                size: 10,
              },
            },
            border: { display: false },
          },
          x: {
            grid: { display: false },
            ticks: {
              color: "#8b5a2b",
              font: {
                family: "Inter",
                size: 11,
              },
            },
            border: { display: false },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true },
        },
      },
    });

    return () => {
      if (barChartRef.current) barChartRef.current.destroy();
    };
  }, [trend.graph]);

  // Doughnut Chart (Demographics)
  useEffect(() => {
    if (!pieRef.current || !trend.demographics) return;
    if (pieChartRef.current) pieChartRef.current.destroy();
    const ctx = pieRef.current.getContext("2d");
    if (!ctx) return;

    const labels = Object.keys(trend.demographics);
    const dataValues = Object.values(trend.demographics);

    pieChartRef.current = new ChartJS(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            data: dataValues,
            backgroundColor: CHART_COLORS.slice(0, 3),
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: "#8b5a2b",
              padding: 12,
              font: {
                family: "Inter",
                size: 11,
              },
            },
          },
          tooltip: { enabled: true },
        },
      },
    });

    return () => {
      if (pieChartRef.current) pieChartRef.current.destroy();
    };
  }, [trend.demographics]);

  const handleImageLoad = (i: number) => {
    setImagesLoaded((prev) => {
      const next = [...prev];
      next[i] = true;
      return next;
    });
  };

  return (
    <>
      <div className="box dashboard-box premium-card">
        {/* Card Header */}
        <div className="premium-header">
          <div className="premium-header-left">
            <span className="premium-header-tag">AI Trend Intelligence Report</span>
            <h2 className="premium-title">{trend.name}</h2>
            <span className="premium-subtitle">
              Pan India · Multi-Signal Forecast {cached && "· (cached)"}
            </span>
          </div>
          <div className="premium-header-right">
            <span className="premium-score-val">{displayScore}</span>
            <span className="premium-score-lbl">TREND SCORE</span>
          </div>
        </div>

        {/* Card Body */}
        <div className="premium-body">
          {/* Badges Row */}
          <div className="premium-badges-row" style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            <span className="premium-badge-momentum" style={{ backgroundColor: stageConfig.bg, color: stageConfig.color, border: `1px solid ${stageConfig.border}` }}>
              ✦ {stageConfig.label}
            </span>
            {trend.category && (
              <span className="premium-badge-invest" style={{ backgroundColor: "#fdfbf7", color: "#50352d", border: "1px solid #d2b48c" }}>
                {trend.category}
              </span>
            )}
            {trend.aesthetic && (
              <span className="premium-badge-invest" style={{ backgroundColor: "#faf5f0", color: "#8b5a2b", border: "1px solid #cba89a" }}>
                {trend.aesthetic}
              </span>
            )}
          </div>

          {/* Trend Description */}
          <p className="premium-trend-desc">{trend.description}</p>

          {/* Consumer Drivers List */}
          {trend.consumer_drivers && trend.consumer_drivers.length > 0 && (
            <div className="drivers-box" style={{ background: "rgba(203, 168, 154, 0.12)", padding: "12px 16px", borderRadius: "8px", margin: "14px 0" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#8b5a2b", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: "6px" }}>
                Key Consumer &amp; Cultural Drivers
              </div>
              <ul style={{ margin: 0, paddingLeft: "18px", color: "#4a3528", fontSize: "13px", lineHeight: "1.5" }}>
                {trend.consumer_drivers.map((drv, dIdx) => (
                  <li key={dIdx}>{drv}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Stacked Layout: Charts & Details */}
          <div className="premium-dashboard-stack">
            {/* Chart 1: Multi-Year Trajectory */}
            <div className="premium-chart-card trajectory-card">
              <h3 className="chart-card-title">Adoption Curve Trajectory</h3>
              <div className="chart-canvas-container">
                <canvas ref={lineRef} id={`lineChart-${index}`}></canvas>
              </div>
            </div>

            {/* Chart 2: Signal Strength */}
            {trend.graph && Object.keys(trend.graph).length > 0 && (
              <div className="premium-chart-card signal-card">
                <h3 className="chart-card-title">Google Trends Velocity</h3>
                <div className="chart-canvas-container">
                  <canvas ref={barRef} id={`barChart-${index}`}></canvas>
                </div>
              </div>
            )}

            {/* Chart 3: Demographics */}
            {trend.demographics && Object.keys(trend.demographics).length > 0 && (
              <div className="premium-chart-card demographics-card">
                <h3 className="chart-card-title">Demographics Split</h3>
                <div className="chart-canvas-container">
                  <canvas ref={pieRef} id={`pieChart-${index}`}></canvas>
                </div>
              </div>
            )}

            {/* Structured Details Stack */}
            <div className="details-stack">
              {trend.targetDemographic && (
                <div className="detail-card">
                  <div className="detail-card-header">
                    <span className="detail-card-icon">🎯</span>
                    <span>Target demographic</span>
                  </div>
                  <div className="detail-card-text">{trend.targetDemographic}</div>
                </div>
              )}

              {trend.peakSeason && (
                <div className="detail-card">
                  <div className="detail-card-header">
                    <span className="detail-card-icon">📅</span>
                    <span>Peak season</span>
                  </div>
                  <div className="detail-card-text">{trend.peakSeason}</div>
                </div>
              )}

              {trend.competitorActivity && (
                <div className="detail-card">
                  <div className="detail-card-header">
                    <span className="detail-card-icon">🏷️</span>
                    <span>Competitor activity</span>
                  </div>
                  <div className="detail-card-text">{trend.competitorActivity}</div>
                </div>
              )}
            </div>
          </div>

          {/* Strategic Merchandising Direction Panel */}
          {(trend.strategic_advice || trend.business) && (
            <div className="premium-invest-panel">
              <span className="premium-invest-title">STRATEGIC MERCHANDISING DIRECTION</span>
              <p className="premium-invest-reason">{trend.strategic_advice || trend.business}</p>
              {trend.risks && (
                <p className="premium-invest-risk">
                  ⚠️ <strong>Risk Assessment:</strong> {trend.risks.startsWith("Risk:") ? "" : " "}{trend.risks}
                </p>
              )}
            </div>
          )}

          {/* Style References Section */}
          {trend.images && trend.images.length > 0 && (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "10px" }}>
              <span className="style-ref-header">VISUAL STYLE REFERENCES</span>
              <div className="style-ref-row">
                {trend.images.slice(0, 3).map((src, i) => (
                  <div
                    key={i}
                    className="style-ref-card"
                    onClick={() => setLightboxSrc(src)}
                  >
                    {!imagesLoaded[i] && <div className="style-reference-skeleton" />}
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={src}
                      alt={`${trend.name} fashion reference ${i + 1}`}
                      className="style-ref-image"
                      style={{ opacity: imagesLoaded[i] ? 1 : 0 }}
                      onLoad={() => handleImageLoad(i)}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Inline lightbox for Unsplash images */}
      {lightboxSrc && (
        <div className="lightbox active" onClick={() => setLightboxSrc(null)}>
          <span className="lightbox-close" onClick={() => setLightboxSrc(null)}>×</span>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={lightboxSrc}
            alt="Expanded view"
            className="lightbox-img"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
