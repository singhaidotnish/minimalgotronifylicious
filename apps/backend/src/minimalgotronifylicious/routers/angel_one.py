# apps/backend/routers/angel_one.py  (keep your existing prefix)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
import time, uuid, os

router = APIRouter(prefix="/api/angel-one", tags=["angel-one"])

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


def get_client():
    use_stub = str(os.getenv("USE_STUB", "true")).lower() == "true"
    if use_stub:
        return _StubClient()
    from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
    from src.minimalgotronifylicious.brokers.order_client_factory import order_client_factory
    sess = AngelOneSession.from_env()
    return order_client_factory("angelone", session=sess)

@router.post("/test")
def test_strategy(group: WireGroup, client = Depends(get_client)):
    """
    Use the real client to fetch LTP as a proof-of-live.
    (Keep the same endpoint the UI already calls.)
    """
    try:
        # pick a symbol from the group if present, else a safe default
        symbol = "NSE:SBIN-EQ"
        for b in group.blocks:
            # if your UI puts symbol in params, grab it
            if "symbol" in b.params:
                symbol = b.params["symbol"]
                break

        ltp = client.ltp(symbol)  # <-- real call now
        return {
            "ok": True,
            "mode": "live" if str(os.getenv("USE_STUB","true")).lower() != "true" else "stub",
            "received": group.model_dump(),
            "ltp": ltp,
            "note": "LIVE SmartAPI call executed via /angel-one/test",
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SmartAPI error: {e}")

@router.get("/health")
def smart_health():
    return {"ok": not _circuit_open(), "note": "adapter ready" if not _circuit_open() else "circuit open"}

@router.post("/login")
def smart_login():
    if _circuit_open():
        raise HTTPException(status_code=503, detail="Circuit open")
    # TODO: call your real Angel One login; for now stub:
    return _ok()

@router.get("/ltp", response_model=LtpResp)
def smart_ltp(symbol: str):
    if _circuit_open():
        raise HTTPException(status_code=503, detail="Circuit open")
    # TODO: replace with real SmartAPI LTP
    price = 100 + (hash(symbol) % 500) / 10.0
    return LtpResp(symbol=symbol, ltp=price, ts=int(time.time() * 1000))

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

@router.get("/ltp")
def smart_ltp(symbol: str, client = Depends(get_client)):
    return client.ltp(symbol)
