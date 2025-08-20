const isServer = typeof window === "undefined";

const apiBaseUrl =
  (isServer
    ? process.env.BACKEND_INTERNAL_URL      // e.g. http://backend:8000 (compose), or Render backend URL
    : process.env.NEXT_PUBLIC_BACKEND_URL   // e.g. http://localhost:5000 (compose), or Render backend URL
  ) || "http://localhost:5000";             // safe fallback, helps dev without Docker

export const APP_CONFIG = {
  apiBaseUrl,
};
