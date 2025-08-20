import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.param_options import PARAM_OPTIONS
from src.minimalgotronifylicious.api import router


# ──────────────────────────────────────────────────────────────────────────────
# Config (single source of truth)
#   • FRONTEND_ORIGINS: comma-separated list of allowed UI origins
#   • DEV_BACKEND_HTTP: public HTTP(S) URL of this API (used in CSP connect-src)
#   • DEV_BACKEND_WS:   public WS(S) URL of this API (used in CSP connect-src)
#   • CORS_ALLOW_METHODS: comma-separated list (e.g., "GET" or "GET,POST,OPTIONS")
#   • CSP_CONNECT_EXTRAS: comma-separated list of extra endpoints for connect-src
#       (use this to allow any temporary ws://localhost:XXXXX or third-party wss)
# ──────────────────────────────────────────────────────────────────────────────

def csv_env(name: str, default: str = "") -> list[str]:
    """ADHD tip: tiny helper to parse comma-separated envs safely."""
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]

def http_to_ws(url: str) -> str:
    if url.startswith("https://"):
        return "wss://" + url[len("https://"):]
    if url.startswith("http://"):
        return "ws://" + url[len("http://"):]
    return url

FRONTEND_ORIGINS = csv_env("FRONTEND_ORIGINS", "http://localhost:3003")
DEV_BACKEND_HTTP = os.getenv("DEV_BACKEND_HTTP", "http://localhost:5000")
DEV_BACKEND_WS   = os.getenv("DEV_BACKEND_WS", "") or http_to_ws(DEV_BACKEND_HTTP)
CORS_ALLOW_METHODS = csv_env("CORS_ALLOW_METHODS", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
CSP_CONNECT_EXTRAS = csv_env("CSP_CONNECT_EXTRAS", "")

# ──────────────────────────────────────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI()

# 1) CORS (env-driven; no hardcoded localhost in code)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_ALLOW_METHODS if CORS_ALLOW_METHODS else ["*"],
    allow_headers=["*"],
)

# 2) CSP (env-driven; one place to allow HTTP + WS connect targets)
def build_csp() -> str:
    connect_src = ["'self'", DEV_BACKEND_HTTP, DEV_BACKEND_WS, *CSP_CONNECT_EXTRAS]
    # De-dup and drop empties
    uniq = []
    for s in connect_src:
        if s and s not in uniq:
            uniq.append(s)
    parts = [
        "default-src 'self'",
        "connect-src " + " ".join(uniq),
        "script-src 'self'",
        "img-src 'self'",
    ]
    return "; ".join(parts) + ";"

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = build_csp()
    return response

# 3) Static file
@app.get("/symbols.json", response_class=FileResponse)
async def serve_symbols():
    # this path is relative to main.py
    symbols_file = Path(__file__).parent / "public" / "symbols.json"
    return FileResponse(symbols_file, media_type="application/json")

# 4) Your other API routers (unchanged)
app.include_router(router)

# 5) Param options (unchanged)
@app.get("/api/param-options")
def get_param_options(type: Optional[str] = None):
    if not type:
        return {"availableTypes": list(PARAM_OPTIONS.keys())}
    if type not in PARAM_OPTIONS:
        return {"error": "Invalid type"}
    return PARAM_OPTIONS[type]

# 6) Health (handy for Docker/Render healthchecks)
@app.get("/health")
def health():
    return {"ok": True}
