/**
 * Resolves the API base URL safely across local and production Vercel environments.
 */
export function getApiBase(): string {
  const envUrl = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");

  // In the browser, if NEXT_PUBLIC_API_URL is localhost or empty, use same-origin relative URLs.
  // This lets Next.js dev server proxy /api/* to http://127.0.0.1:5000 without CORS or IPv6 binding issues,
  // and allows Vercel deployments to route /api/* directly.
  if (typeof window !== "undefined") {
    const isLocalhostEnv = envUrl.includes("localhost") || envUrl.includes("127.0.0.1");
    if (!envUrl || isLocalhostEnv) {
      return "";
    }
  }

  return envUrl;
}

export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const base = getApiBase();
  return base ? `${base}${cleanPath}` : cleanPath;
}

export const API_BASE = getApiBase();

