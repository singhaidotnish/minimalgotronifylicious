# src/minimalgotronifylicious/routers/angel_one.py
from __future__ import annotations

import os
import time
import uuid
import logging
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Body
from pydantic import BaseModel, Field

from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory

router = APIRouter(prefix="/api", tags=["angel-one"])
log = logging.getLogger("uvicorn")

# ---------------------------
# helpers: mode / circuit / utils
# ---------------------------
def _get_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

def paper_mode() -> bool:
    # New flag wins; keep temporary back-compat with USE_STUB
    if "PAPER_TRADING" in os.environ:
        return _get_bool("PAPER_TRADING", False)
    if "USE_STUB" in os.environ:  # deprecated
        log.warning("USE_STUB is deprecated; use PAPER_TRADING=true/false")
        return _get_bool("USE_STUB", False)
    return False

_failures = 0
_open_until_ms = 0

def _circuit_open() -> bool:
    return time.time() * 1000 < _open_until_ms

def _record_failure(threshold=5, reset_ms=30_000):
    global _failures, _open_until_ms
    _failures += 1
    if _failures >= threshold:
        _open_until_ms = int(time.time() * 1000) + reset_ms
        _failures = 0

def _record_success():
    global _failures
    _failures = 0

def _now_ms() -> int:
    return int(time.time() * 1000)

def _normalize_symbol(raw: str, default_ex="NSE") -> tuple[str, str, str]:
    """
    Accepts 'NSE:SBIN-EQ' or 'SBIN-EQ' and returns (exchange, token, combined).
    """
    s = (raw or "").strip().upper()
    if ":" in s:
        ex, token = s.split(":", 1)
        ex = ex or default_ex
    else:
        ex, token = default_ex, s
    return ex, token, f"{ex}:{token}"

# ---------------------------
# DI: get client (paper/live via Factory)
# ---------------------------
def get_client():
    if paper_mode():
        # Factory returns PaperClient when PAPER_TRADING=true
        return OrderClientFactory.create("angel_one", session=None)

    # Live path: import here to avoid circulars / import costs in paper mode
    from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
    sess = AngelOneSession.from_env()
    return OrderClientFactory.create("angel_one", session=sess)

# ---------------------------
# Models
# ---------------------------
class LtpResp(BaseModel):
    symbol: str = Field(..., description="Symbol as requested (e.g., NSE:SBIN-EQ)")
    ltp: float
    ts: int

class OrderRequest(BaseModel):
    symbol: str
    qty: int
    side: Literal["BUY", "SELL"] = "BUY"
    type: Literal["MARKET", "LIMIT"] = "MARKET"
    price: Optional[float] = None

class OrderResp(BaseModel):
    orderId: str
    status: Literal["ACCEPTED", "REJECTED", "PENDING"]
    message: Optional[str] = None

# ---------------------------
# Routes
# ---------------------------
@router.get("/health")
def smart_health():
    """
    Health for docker-compose (200 OK).
    """
    return {"status": "ok" if not _circuit_open() else "degraded", "circuit_open": _circuit_open()}

@router.get("/mode")
def mode():
    return {"mode": "paper" if paper_mode() else "live"}

@router.get("/ltp", response_model=LtpResp)
def ltp(symbol: str, client = Depends(get_client)):
    ex, token, combined = _normalize_symbol(symbol)
    try:
        raw = client.ltp(combined)  # some adapters accept combined
    except TypeError:
        raw = client.ltp(exchange=ex, symbol=token)  # others want kwargs

    px = _extract_price(raw)
    return LtpResp(symbol=combined, ltp=px, ts=_now_ms())


# minimal in-memory idempotency for /order
_IDEM: Dict[str, Dict[str, Any]] = {}

@router.post("/order", response_model=OrderResp)
def place_order(
    req: OrderRequest,
    client = Depends(get_client),
    request_id: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Request-Id"),
):
    """
    Idempotent order placement using X-Request-Id.
    Paper mode returns a stub response; live mode should call client.place_order(...)
    """
    if _circuit_open():
        raise HTTPException(status_code=503, detail="Circuit open")
    if not request_id:
        raise HTTPException(status_code=400, detail="Missing X-Request-Id")

    key = f"order:{request_id}"
    if key in _IDEM:
        return _IDEM[key]

    # Paper: fake accept; Live: call real adapter
    if paper_mode():
        resp = OrderResp(orderId=str(uuid.uuid4()), status="ACCEPTED", message="stubbed (paper mode)").model_dump()
    else:
        # Map to your live adapter contract; adjust as needed
        try:
            payload = req.model_dump() if hasattr(req, "model_dump") else req.dict()
            result = client.place_order(**payload)
            # Normalize a few common fields if possible
            order_id = str(result.get("order_id") or result.get("orderId") or uuid.uuid4())
            status = str(result.get("status") or "ACCEPTED").upper()
            message = result.get("message")
            resp = OrderResp(orderId=order_id, status=status, message=message).model_dump()
        except Exception as e:
            _record_failure()
            raise HTTPException(status_code=502, detail=f"Broker error: {type(e).__name__}: {e}") from e

    _record_success()
    _IDEM[key] = resp
    return resp

@router.get("/positions")
def positions(client = Depends(get_client)):
    """
    Paper: returns in-memory snapshot if available.
    Live: call adapter's positions/holdings as you wire it.
    """
    if _circuit_open():
        raise HTTPException(status_code=503, detail="Circuit open")

    if hasattr(client, "snapshot"):
        try:
            snap = client.snapshot()
            return {"status": "ok", "snapshot": snap}
        except Exception as e:
            _record_failure()
            raise HTTPException(status_code=502, detail=f"Snapshot error: {e}") from e

    # fallback if adapter doesn't implement snapshot
    return {"status": "ok", "positions": []}

@router.post("/angel-one/test")
def test_strategy(payload: Dict[str, Any] = Body(...), client = Depends(get_client)):
    mode = "paper" if paper_mode() else "live"
    raw = payload.get("symbol") or payload.get("scrip") or payload.get("token") or "SBIN-EQ"
    ex = payload.get("exchange") or "NSE"
    _, _, combined = _normalize_symbol(f"{ex}:{raw}")

    try:
        try:
            raw_ltp = client.ltp(combined)
        except TypeError:
            raw_ltp = client.ltp(exchange=ex, symbol=raw)

        ltp_val = _extract_price(raw_ltp)
        _record_success()
        return {
            "status": "ok",
            "mode": mode,
            "used_symbol": combined,
            "received": payload,
            "ltp": ltp_val,
            "note": "STUB adapter executed" if mode == "paper" else "LIVE SmartAPI call executed",
        }
    except Exception as e:
        _record_failure()
        log.exception("test_strategy failed")
        # include a hint about the shape, if we can
        detail = getattr(e, "args", [str(e)])[0]
        raise HTTPException(status_code=502, detail=f"{type(e).__name__}: {detail}")


def _extract_price(val: Any) -> float:
    """
    Accepts number | string | dict | list and extracts a float price.
    Common shapes handled:
      - 123.45
      - "123.45"
      - {"ltp": 123.45}
      - {"price": 123.45} / {"last_price": 123.45}
      - {"symbol":"NSE:SBIN-EQ","ltp":123.45}
      - {"data": {"ltp": 123.45}} or deeper nested dicts
      - [{"ltp": 123.45}, ...]  (takes first)
    """
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        return float(val.strip())

    if isinstance(val, dict):
        # direct keys first
        for k in ("ltp", "price", "last_price", "LastTradedPrice", "closePrice"):
            if k in val:
                try:
                    return float(val[k])
                except Exception:
                    pass
        # nested hunt (breadth-first-ish)
        for v in val.values():
            try:
                return _extract_price(v)
            except Exception:
                continue

    if isinstance(val, (list, tuple)) and val:
        try:
            return _extract_price(val[0])
        except Exception:
            pass

    raise TypeError(f"Could not extract price from value of type {type(val).__name__}: {val!r}")
