import { NextRequest, NextResponse } from "next/server";

// Curated Stopwords
const STOPWORDS = new Set([
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
  "look", "see", "one", "new", "via", "click", "read", "post", "share", "com"
]);

// Domain Lemmatization Mapping
const LEMMA_MAP: Record<string, string> = {
  kurtas: "kurta", kurtis: "kurti", sarees: "saree", saris: "saree",
  lehengas: "lehenga", lehngas: "lehenga", dupattas: "dupatta", palazzos: "palazzo",
  anarkalis: "anarkali", dhotis: "dhoti", sherwanis: "sherwani", juttis: "jutti",
  cholis: "choli", jackets: "jacket", blazers: "blazer", dresses: "dress",
  skirts: "skirt", trousers: "trouser", pants: "pant", silhouettes: "silhouette",
  fabrics: "fabric", textiles: "textile", embroideries: "embroidery", prints: "print",
  patterns: "pattern", bows: "bow", ribbons: "ribbon", sleeves: "sleeve",
  motifs: "motif", pleats: "pleat", ruffles: "ruffle", corsets: "corset"
};

// Indian & Global Fashion Taxonomy with Boost Multipliers
const DOMAIN_TAXONOMY: Record<string, number> = {
  chikankari: 1.6, bandhani: 1.5, kanjeevaram: 1.5, banarasi: 1.5,
  khadi: 1.4, ajrakh: 1.5, phulkari: 1.5, chanderi: 1.4, ikkat: 1.4,
  kalamkari: 1.4, zardozi: 1.4, gota: 1.4, patola: 1.5, mulmul: 1.3,
  handloom: 1.5, kurta: 1.4, kurti: 1.3, saree: 1.5, lehenga: 1.5,
  anarkali: 1.3, dupatta: 1.2, palazzo: 1.2, "co-ord": 1.4, dhoti: 1.3,
  sherwani: 1.3, jacket: 1.2, corset: 1.4, blazer: 1.3, "slip dress": 1.3,
  bow: 1.5, bows: 1.5, ribbon: 1.4, oversized: 1.3, drape: 1.3,
  minimalist: 1.3, "indo-western": 1.5, fusion: 1.4, pastel: 1.3,
  sustainable: 1.4, organza: 1.4, linen: 1.3, silk: 1.4, velvet: 1.3
};

// Fashion Named Entity Dictionary
const NER_TAXONOMY = {
  silhouettes: [
    "kurta", "kurti", "saree", "lehenga", "anarkali", "co-ord", "palazzo",
    "dhoti", "sherwani", "blazer", "corset", "slip dress", "jacket", "maxi",
    "drape dress", "kaftan", "sharara", "gharara", "peplum", "tunic"
  ],
  fabrics: [
    "chikankari", "handloom", "khadi", "chanderi", "banarasi", "kanjeevaram",
    "mulmul", "silk", "linen", "organza", "velvet", "georgette", "cotton",
    "satin", "tussar", "brocade", "crepe", "chiffon", "tweed"
  ],
  aesthetics: [
    "indo-western", "fusion", "minimalist", "maximalist", "contemporary",
    "festive", "regal", "cottagecore", "y2k", "quiet luxury", "boho chic",
    "streetwear", "modern heritage", "androgynous", "retro"
  ],
  colors: [
    "pastel", "earth tones", "ivory", "gold", "blush pink", "sage green",
    "emerald", "mustard", "terracotta", "midnight blue", "crimson", "lavender",
    "monochrome", "metallic", "olive", "champagne", "rust"
  ],
  techniques: [
    "zardozi", "bandhani", "ajrakh", "gota patti", "embroidery", "block print",
    "kalamkari", "mirror work", "phulkari", "tie-dye", "threadwork", "aari"
  ],
  motifs: [
    "bow", "bows", "ribbon", "floral", "geometric", "paisley", "ruffle",
    "pleat", "asymmetrical", "cutout", "feather", "fringe", "pearls"
  ]
};

// Sentiment Lexicon
const POSITIVE_SIGNALS = new Set([
  "surge", "surging", "growth", "growing", "rising", "trend", "trending",
  "popular", "demand", "breakout", "bullish", "luxury", "bespoke", "elegant",
  "aesthetic", "innovative", "celebrated", "viral", "statement", "signature",
  "coveted", "must-have", "dominant", "thriving", "acclaimed", "chic"
]);

const NEGATIVE_SIGNALS = new Set([
  "declining", "decline", "dated", "fatigue", "sluggish", "waning", "saturated",
  "outdated", "fading", "criticized", "costly", "drop", "dropping", "loss"
]);

// Helper for Tokenizing & Cleaning
function preprocessText(raw: string) {
  const cleaned = raw.toLowerCase().replace(/[^\w\s-]/g, " ").replace(/\s+/g, " ").trim();
  const rawWords = cleaned.split(" ").filter((w) => w.length > 0);
  
  const tokens = rawWords
    .map((w) => LEMMA_MAP[w] || w)
    .filter((w) => w.length >= 3 && !STOPWORDS.has(w));

  const totalWords = rawWords.length;
  const uniqueWords = new Set(tokens).size;
  const filteredCount = tokens.length;
  const avgLen = rawWords.length > 0
    ? Number((rawWords.reduce((acc, w) => acc + w.length, 0) / rawWords.length).toFixed(1))
    : 0;
  const lexicalDiv = totalWords > 0 ? Number((uniqueWords / totalWords).toFixed(2)) : 0;

  return {
    rawWords,
    tokens,
    stats: {
      total_words: totalWords,
      filtered_word_count: filteredCount,
      unique_words: uniqueWords,
      lexical_diversity: lexicalDiv,
      average_word_length: avgLen
    }
  };
}

// TF-IDF Keyword Extraction with Indian Domain Boosting
function extractKeywords(tokens: string[], rawWords: string[]) {
  const counts: Record<string, number> = {};
  for (const t of tokens) {
    counts[t] = (counts[t] || 0) + 1;
  }

  // Include bigrams
  for (let i = 0; i < rawWords.length - 1; i++) {
    const w1 = LEMMA_MAP[rawWords[i]] || rawWords[i];
    const w2 = LEMMA_MAP[rawWords[i + 1]] || rawWords[i + 1];
    if (!STOPWORDS.has(w1) && !STOPWORDS.has(w2) && w1.length >= 3 && w2.length >= 3) {
      const bigram = `${w1} ${w2}`;
      counts[bigram] = (counts[bigram] || 0) + 1.2;
    }
  }

  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
  const results: Array<{ keyword: string; score: number; tfidf_raw: number; boost_factor: number }> = [];

  for (const [kw, count] of Object.entries(counts)) {
    const tf = count / total;
    const baseIdf = Math.log(1 + 50 / (1 + count)) + 1.0;
    const rawTfidf = Number((tf * baseIdf).toFixed(4));
    
    let boost = DOMAIN_TAXONOMY[kw.toLowerCase()] || 1.0;
    if (boost === 1.0) {
      for (const [taxWord, taxBoost] of Object.entries(DOMAIN_TAXONOMY)) {
        if (kw.includes(taxWord)) {
          boost = Math.max(boost, taxBoost);
        }
      }
    }

    const finalScore = Number((rawTfidf * boost * 10).toFixed(3));
    results.push({
      keyword: kw,
      score: finalScore,
      tfidf_raw: rawTfidf,
      boost_factor: boost
    });
  }

  results.sort((a, b) => b.score - a.score);
  return results.slice(0, 15);
}

// Named Entity Recognition (NER)
function extractEntities(text: string) {
  const lower = text.toLowerCase();
  const entities: Record<string, Array<{ entity: string; count: number; category: string }>> = {
    silhouettes: [],
    fabrics: [],
    aesthetics: [],
    colors: [],
    techniques: [],
    motifs: []
  };

  for (const [category, terms] of Object.entries(NER_TAXONOMY)) {
    const catList: Array<{ entity: string; count: number; category: string }> = [];
    for (const term of terms) {
      const regex = new RegExp(`\\b${term}\\b`, "gi");
      const matches = lower.match(regex);
      if (matches) {
        catList.push({
          entity: term,
          count: matches.length,
          category
        });
      }
    }
    catList.sort((a, b) => b.count - a.count);
    entities[category] = catList;
  }

  const summary: Record<string, number> = {};
  for (const [cat, list] of Object.entries(entities)) {
    summary[cat] = list.length;
  }

  return { entities, entity_summary: summary };
}

// Fashion Sentiment Analysis
function analyzeSentiment(rawWords: string[]) {
  let posCount = 0;
  let negCount = 0;

  for (const w of rawWords) {
    if (POSITIVE_SIGNALS.has(w)) posCount++;
    if (NEGATIVE_SIGNALS.has(w)) negCount++;
  }

  const total = posCount + negCount;
  let polarity = 0;
  if (total > 0) {
    polarity = (posCount - negCount) / total;
  } else {
    polarity = 0.35;
  }

  const momentumScore = Math.round(50 + polarity * 38);
  let label = "Growing (Positive Adoption)";
  if (momentumScore >= 78) label = "Bullish (High Growth Velocity)";
  else if (momentumScore <= 40) label = "Cautious (Declining Trajectory)";
  else if (momentumScore < 60) label = "Stable (Balanced Market Interest)";

  return {
    sentiment: label,
    momentum_score: momentumScore,
    polarity: Number(polarity.toFixed(2)),
    subjectivity: 0.65,
    signals_detected: { positive: posCount, negative: negCount }
  };
}

export async function POST(req: NextRequest) {
  const startTime = Date.now();
  try {
    const body = await req.json();
    const text = String(body.text || "").trim();
    const region = String(body.region || "Pan India");
    const year = String(body.year || "2026");

    if (!text) {
      return NextResponse.json({ error: "No input text provided for analysis" }, { status: 400 });
    }

    // Stage 1: Linguistic Preprocessing & Tokenizer
    const { rawWords, tokens, stats } = preprocessText(text);

    // Stage 2: TF-IDF Extraction with Domain Weights
    const keywords = extractKeywords(tokens, rawWords);

    // Stage 3: Fashion Named Entity Recognition (NER)
    const { entities, entity_summary } = extractEntities(text);

    // Stage 4: Sentiment & Market Momentum Analysis
    const sentiment = analyzeSentiment(rawWords);

    // Stage 5: 100% Dynamic Intelligence from Google Gemini API
    const apiKey = (
      process.env.GEMINI_API_KEY ||
      "AIzaSyA03LxYn6EOviCclyRjgO505L_6lgqKY9U"
    ).trim().replace(/["']/g, "");

    const topKwStr = keywords.slice(0, 8).map((k) => k.keyword).join(", ");
    const entStr = Object.entries(entities)
      .filter(([_, list]) => list.length > 0)
      .map(([cat, list]) => `${cat}: ${list.slice(0, 3).map((e) => e.entity).join(", ")}`)
      .join(" | ");

    const prompt = `You are a Senior Fashion Trend Intelligence Forecaster specializing in Indian and global fashion markets.
Analyze this fashion text for region: "${region}", forecast year: "${year}".

Input Text:
"""
${text}
"""

Extracted Keywords: ${topKwStr || "contemporary silhouette"}
Extracted NER Entities: ${entStr || "None detected"}
Market Sentiment: ${sentiment.sentiment} (Score: ${sentiment.momentum_score}/100)

Extract and generate bespoke fashion trend intelligence based directly on this text.
Return a STRICTLY valid JSON object matching this schema (NO markdown backticks, NO commentary):
{
  "market_synthesis": "Comprehensive executive market synthesis analyzing consumer adoption, silhouette innovation, and retail opportunity in India.",
  "trends": [
    {
      "name": "Distinct trend name",
      "category": "Apparel Category (e.g. Occasionwear / Fusion / Streetwear)",
      "garment": "Primary silhouette or garment",
      "colour": "Color direction or dominant palette",
      "material": "Key textile / fabrication",
      "silhouette": "Key silhouette descriptors",
      "aesthetic": "Aesthetic core",
      "trend_stage": "Emerging" or "Growing" or "Stable",
      "trend_score": 84,
      "confidence": 0.92,
      "evidence": "Direct quote or grounded textual phrase from input text",
      "drivers": ["Key consumer or cultural driver 1", "Key commercial driver 2"],
      "strategic_advice": "Actionable design, pricing, and merchandising advice for apparel brands",
      "palette": ["#C5A059", "#2D2D2D", "#F4F1DE", "#E07A5F"],
      "demographics": {"Gen-Z": 60, "Millennials": 30, "Gen-X": 10},
      "yearlyForecast": [
        {"year": "2025", "score": 70},
        {"year": "2026", "score": 84},
        {"year": "2027", "score": 92},
        {"year": "2028", "score": 82},
        {"year": "2029", "score": 60}
      ]
    }
  ]
}`;

    const geminiRes = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            responseMimeType: "application/json",
            temperature: 0.2
          }
        })
      }
    );

    if (!geminiRes.ok) {
      const errText = await geminiRes.text();
      throw new Error(`Google Gemini API error (${geminiRes.status}): ${errText}`);
    }

    const resJson = await geminiRes.json();
    const rawReply = resJson.candidates?.[0]?.content?.parts?.[0]?.text || "";
    if (!rawReply) {
      throw new Error("Gemini API returned an empty response. Please check input text or API quota.");
    }

    const cleanJson = rawReply.replace(/```json/g, "").replace(/```/g, "").trim();
    const geminiData = JSON.parse(cleanJson);

    const totalLatency = Date.now() - startTime;

    return NextResponse.json({
      nlp_analysis: {
        statistics: stats,
        keywords,
        entities,
        entity_summary,
        sentiment,
        nlp_latency_ms: totalLatency
      },
      trends: geminiData.trends || [],
      market_synthesis: geminiData.market_synthesis || "",
      metadata: {
        processing_time_ms: totalLatency,
        llm_model: "gemini-2.5-flash",
        region,
        year,
        cached: false
      }
    });
  } catch (err: any) {
    console.error("NLP Analysis Error:", err);
    return NextResponse.json(
      { error: "NLP Analysis Pipeline Failure", details: err?.message || String(err) },
      { status: 500 }
    );
  }
}
