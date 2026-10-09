/**
 * Resolves API endpoints.
 * Always returns relative paths (e.g. "/api/forecast", "/api/analyze")
 * so that both local Next.js dev server and deployed Vercel apps route correctly.
 */
export function getApiBase(): string {
  const envUrl = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");
  // Ignore localhost or 127.0.0.1 in production to prevent browser connection errors
  if (envUrl && !envUrl.includes("localhost") && !envUrl.includes("127.0.0.1")) {
    return envUrl;
  }
  return "";
}

export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const base = getApiBase();
  return base ? `${base}${cleanPath}` : cleanPath;
}

export const API_BASE = "";

