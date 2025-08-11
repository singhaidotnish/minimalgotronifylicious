from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.param_options import PARAM_OPTIONS


app = FastAPI()

# 1) CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_methods=["GET"],
  allow_headers=["*"],
)

# 2) CSP
@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "connect-src 'self' http://localhost:5001 "
        "wss://minimalgotronifylicious-backend.up.railway.app "
        "ws://127.0.0.1:46630 "
        "script-src 'self'; "
        "img-src 'self';"
    )
    return response

@app.get("/symbols.json", response_class=FileResponse)
async def serve_symbols():
    # this path is relative to main.py
    symbols_file = Path(__file__).parent / "public" / "symbols.json"
    return FileResponse(symbols_file, media_type="application/json")

# 4) Your other API routers
from src.minimalgotronifylicious.api import router
app.include_router(router)


@app.get("/api/param-options")
def get_param_options(type: str = None):
    if not type:
        return {"availableTypes": list(PARAM_OPTIONS.keys())}
    if type not in PARAM_OPTIONS:
        return {"error": "Invalid type"}
    return PARAM_OPTIONS[type]
