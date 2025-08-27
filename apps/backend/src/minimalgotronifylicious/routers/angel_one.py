# apps/backend/routers/angel_one.py  (keep your existing prefix)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
import os, time, uuid, logging

router = APIRouter(prefix="/api/angel-one", tags=["angel-one"])
log = logging.getLogger("uvicorn")

# --- existing models (keep) ---
class WireCondition(BaseModel):
    keyword: str
    params: Dict[str, str] = Field(default_factory=dict)
    label: str

class WireGroup(BaseModel):
    logic: Literal["AND", "OR"]
    blocks: List[WireCondition]

# --- add real trading models/endpoints below ---
class LtpResp(BaseModel):
    symbol: str
    ltp: float
    ts: int  # epoch ms

class OrderRequest(BaseModel):
    symbol: str
    qty: int
    side: Literal["BUY", "SELL"]
    type: Literal["MARKET", "LIMIT"]
    price: Optional[float] = None

class OrderResp(BaseModel):
    orderId: str
    status: Literal["ACCEPTED", "REJECTED", "PENDING"]
    message: Optional[str] = None

_USE_STUB = str(os.getenv("USE_STUB", "true")).lower() == "true"
_failures = 0
_open_until = 0  # epoch ms

def _circuit_open() -> bool:
    return time.time() * 1000 < _open_until

def _ok():  # tiny helper
    return {"ok": True}

# --- lightweight stub that mirrors the live client surface ---
class _StubClient:
    def __init__(self):
        self._logged_in = False

    # keep the same method names the live client uses
    def login(self):
        self._logged_in = True
        return {"ok": True, "mode": "stub"}

    def ltp(self, *args, **kwargs):
        """
        Accepts either ltp("NSE:SBIN-EQ") OR ltp(exchange="NSE", symbol="SBIN").
        Returns a float (so router can wrap it in your response model).
        """
        if args and isinstance(args[0], str):
            symbol = args[0]
        else:
            ex = kwargs.get("exchange") or "NSE"
            sym = kwargs.get("symbol") or "SBIN"
            symbol = f"{ex}:{sym}"
        # deterministic but fake price for UI/demo/tests
        return 100 + (hash(symbol) % 500) / 10.0

    def order(self, **kwargs):
        # pretend we placed an order and return an id
        import uuid
        return {"orderId": str(uuid.uuid4()), "status": "ACCEPTED"}

    def positions(self):
        return []

    def logout(self):
        self._logged_in = False
        return {"ok": True}

def get_client():
    # feature-flag toggle
    if str(os.getenv("USE_STUB", "true")).lower() == "true":
        from ._stub_client import StubClient  # your stub class
        return StubClient()

    # LIVE
    required = ["SMARTAPI_API_KEY","SMARTAPI_CLIENT_CODE","SMARTAPI_TOTP_SECRET"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise HTTPException(500, f"Missing env: {', '.join(missing)}")

    sess = AngelOneSession.from_env()
    return order_client_factory("angelone", session=sess)

@router.get("/ltp")
def ltp(symbol: str, client = Depends(get_client)):
    try:
        return {"symbol": symbol, "ltp": float(client.ltp(symbol))}
    except TypeError:
        ex, ts = (symbol.split(":", 1) + [""])[:2]
        return {"symbol": symbol, "ltp": float(client.ltp(exchange=ex or "NSE", symbol=ts or symbol))}

def _pick_symbol(group: WireGroup) -> str:
    # Try to pull from block params; else default
    for b in group.blocks:
        s = (b.params.get("symbol") or b.params.get("tradingsymbol") or "").strip()
        if s:
            return s
    return "NSE:SBIN-EQ"  # safe default for testing

def _normalize_symbol(sym: str):
    # Accept "NSE:SBIN-EQ" or "SBIN" → return tuple (exchange, tradingsymbol, combined)
    if ":" in sym:
        ex, ts = sym.split(":", 1)
        return ex.strip(), ts.strip(), sym
    return "NSE", sym.strip(), f"NSE:{sym.strip()}"

@router.post("/test")
def test_strategy(group: WireGroup, client = Depends(get_client)):
    mode = "live" if str(os.getenv("USE_STUB","true")).lower() != "true" else "stub"
    use_stub = str(os.getenv("USE_STUB","true")).lower() == "true"
    mode = "stub" if use_stub else "live"
    try:
        # If this is a live client, ensure it’s authenticated
        if mode == "live" and hasattr(client, "login"):
            client.login()  # no-op for stub; real client should create session

        raw_sym = _pick_symbol(group)
        exchange, tradingsymbol, combined = _normalize_symbol(raw_sym)

        # Try a robust LTP call — adapt to your client's method signature
        if hasattr(client, "ltp"):
            try:
                ltp = client.ltp(combined)  # if your client accepts "NSE:SBIN-EQ"
            except TypeError:
                # some clients require separate args
                ltp = client.ltp(exchange=exchange, symbol=tradingsymbol)
        else:
            raise RuntimeError("Client has no ltp() method")

        return {
            "ok": True,
            "mode": mode,
            "used_symbol": combined,
            "received": group.model_dump(),
            "ltp": ltp,
            "note": "STUB adapter executed" if use_stub else "LIVE SmartAPI call executed",
        }

    except HTTPException:
        raise
    except Exception as e:
        log.exception("test_strategy failed")
        # return a detailed body so the UI shows it
        raise HTTPException(status_code=502, detail=f"{type(e).__name__}: {e}")

@router.get("/health")
def smart_health():
    return {"ok": not _circuit_open(), "note": "adapter ready" if not _circuit_open() else "circuit open"}

@router.post("/login")
def smart_login():
    if _circuit_open():
        raise HTTPException(status_code=503, detail="Circuit open")
    # TODO: call your real Angel One login; for now stub:
    return _ok()

@router.post("/order", response_model=OrderResp)
def smart_order(req: OrderRequest):
    if _circuit_open():
        raise HTTPException(status_code=503, detail="Circuit open")
    # TODO: replace with real order placement
    return OrderResp(orderId=str(uuid.uuid4()), status="ACCEPTED", message="stubbed")

@router.get("/positions")
def smart_positions():
    if _circuit_open():
        raise HTTPException(status_code=503, detail="Circuit open")
    # TODO: replace with real positions call
    return {"ok": True, "positions": []}

@router.post("/logout")
def smart_logout():
    return _ok()

@router.get("/mode")
def mode():
    use_stub = str(os.getenv("USE_STUB", "true")).lower() == "true"
    return {"mode": "stub" if use_stub else "live"}
