from __future__ import annotations
import os, uuid
import time, logging
from typing import Optional, Literal, Any, Dict

from fastapi import APIRouter, Depends, Header, HTTPException, Body
from pydantic import BaseModel, Field

from src.minimalgotronifylicious.brokers.order_client_factory import (
    order_client_factory, resolve_broker_name
)
from src.minimalgotronifylicious.utils.circuit_breaker import Circuit
from src.minimalgotronifylicious.utils.symbols import normalize
from src.minimalgotronifylicious.utils.price import extract_price
from src.minimalgotronifylicious.utils.broker_registry import get_symbols_provider
from src.minimalgotronifylicious.deps.broker import client_dep


router = APIRouter(prefix="/api", tags=["trading"])
log = logging.getLogger("uvicorn")

circuit = Circuit()
_IDEM: Dict[str, Dict[str, Any]] = {}
# ---------------------------
# helpers: mode / circuit / utils
# ---------------------------

_failures = 0
_open_until_ms = 0

# minimal in-memory idempotency for /order
_IDEM: Dict[str, Dict[str, Any]] = {}
# ---------------------------
# Models
# ---------------------------

class LtpResp(BaseModel):
    symbol: str
    ltp: float
    ts: int

class OrderRequest(BaseModel):
    symbol: str
    qty: float
    side: Literal["BUY","SELL"] = "BUY"
    type: Literal["MARKET","LIMIT"] = "MARKET"
    price: Optional[float] = None

class OrderResp(BaseModel):
    orderId: str
    status: Literal["ACCEPTED","REJECTED","PENDING"]
    message: Optional[str] = None

@router.get("/symbols")
def symbols(
    x_broker: Optional[str] = Header(default=None, convert_underscores=False),
    x_market_open: Optional[str] = Header(default=None, convert_underscores=False),
):
    market_open = (x_market_open or "").strip().lower() in ("1","true","yes","on")
    name = resolve_broker_name(x_broker or os.getenv("BROKER","auto"), market_open)
    provider = get_symbols_provider(name)
    return {"broker": name, "items": provider()}

@router.get("/ltp", response_model=LtpResp)
def ltp(symbol: str, client = Depends(client_dep)):
    ex, token, combined = normalize(symbol)
    try:
        raw = client.ltp(combined)
    except TypeError:
        raw = client.ltp(exchange=ex, symbol=token)
    return LtpResp(symbol=combined, ltp=extract_price(raw), ts=__import__("time").time_ns()//1_000_000)

@router.post("/order", response_model=OrderResp)
def order(
    req: OrderRequest,
    client = Depends(client_dep),
    request_id: Optional[str] = Header(default=None, convert_underscores=False, alias="X-Request-Id"),
):
    if circuit.open():
        raise HTTPException(status_code=503, detail="Circuit open")
    if not request_id:
        raise HTTPException(status_code=400, detail="Missing X-Request-Id")

    key = f"order:{request_id}"
    if key in _IDEM:
        return _IDEM[key]

    # Paper/live distinction is inside the adapter or via env; just try
    try:
        result = place_order(**(req.model_dump() if hasattr(req, "model_dump") else req.dict()))
        order_id = str(result.get("order_id") or result.get("orderId") or uuid.uuid4())
        status = str(result.get("status") or "ACCEPTED").upper()
        message = result.get("message")
        resp = OrderResp(orderId=order_id, status=status, message=message).model_dump()
        circuit.ok()
    except Exception as e:
        circuit.fail()
        raise HTTPException(status_code=502, detail=f"Broker error: {type(e).__name__}: {e}") from e

    _IDEM[key] = resp
    return resp


def _circuit_open() -> bool:
    return time.time() * 1000 < _open_until_ms


@router.get("/health")
def smart_health():
    """
    Health for docker-compose (200 OK).
    """
    return {"status": "ok" if not _circuit_open() else "degraded", "circuit_open": _circuit_open()}


def paper_mode() -> bool:
    # If env forces paper, return True; otherwise false (AUTO decided in factory)
    from src.minimalgotronifylicious.brokers.order_client_factory import _paper_env_enabled
    return _paper_env_enabled()


def get_client(
    x_broker: Optional[str] = Header(default=None, convert_underscores=False),
    x_market_open: Optional[str] = Header(default=None, convert_underscores=False),
):
    """
    Priority:
      1) X-Broker: 'angel_one' | 'binance' | 'paper_trade' | 'auto'
      2) env BROKER (defaults to 'auto')
    For 'auto', we use X-Market-Open: 'true' | 'false' from the UI.
    """
    # normalize inputs
    broker = (x_broker or os.getenv("BROKER", "auto")).strip().lower().replace("-", "_")
    market_open = None
    if x_market_open is not None:
        market_open = x_market_open.strip().lower() in ("1","true","yes","on")

    try:
        # Angel One uses session; factory will validate envs
        if broker == "angel_one":
            from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
            sess = AngelOneSession.from_env()
            return order_client_factory("angel_one", session=sess)

        # Others don't need session; pass flags for AUTO
        return order_client_factory(broker, market_open=market_open)

    except RuntimeError as e:
        # Missing creds etc.
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _record_failure(threshold=5, reset_ms=30_000):
    global _failures, _open_until_ms
    _failures += 1
    if _failures >= threshold:
        _open_until_ms = int(time.time() * 1000) + reset_ms
        _failures = 0


def _record_success():
    global _failures
    _failures = 0


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


@router.get("/mode")
def mode():
    return {"mode": "paper" if paper_mode() else "live"}


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
