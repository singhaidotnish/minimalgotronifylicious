// apps/ui/src/lib/urls.ts  (or apps/ui/lib/urls.ts)
export const API_BASE =
  (typeof window === "undefined"
    ? process.env.BACKEND_INTERNAL_URL   // SSR / API routes (inside Docker: http://backend:8000)
    : process.env.NEXT_PUBLIC_BACKEND_URL // Browser (host-mapped: http://localhost:5000)
  ) || "http://localhost:5000"; // safe fallback
