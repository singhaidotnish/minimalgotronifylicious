# apps/backend/routers/options.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Literal, Optional, List, Dict, Any
import os, time

router = APIRouter(prefix="/api/options", tags=["options"])

# ---------- models (shared shapes for UI) ----------
Side = Literal["CE", "PE"]
ExpirySel = Literal["current_week", "next_week", "monthly", "custom"]
StrikeSel = Literal["ATM", "OTM+steps", "ITM+steps", "ByStrike"]

class ChainRow(BaseModel):
    tradingsymbol: str
    exchange: str
    strike: float
    side: Side
    expiry: str    # YYYY-MM-DD
    ltp: float
    iv: Optional[float] = None
    oi: Optional[int] = None
    bid: Optional[float] = None
    ask: Optional[float] = None

class ChainResp(BaseModel):
    underlying: str
    expiry: str
    rows: List[ChainRow]

class ResolveReq(BaseModel):
    underlying: str
    side: Side
    strikeSel: StrikeSel
    steps: Optional[int] = None
    strike: Optional[float] = None
    expirySel: ExpirySel
    expiry: Optional[str] = None  # YYYY-MM-DD if custom

class ResolveResp(BaseModel):
    tradingsymbol: str
    exchange: str

class ValueResp(BaseModel):
    symbol: str
    field: Literal["ltp", "iv", "oi"]
    value: float
    ts: int

class GreekResp(BaseModel):
    symbol: str
    delta: float
    gamma: float
    theta: float
    vega: float
    ts: int

# ---------- client plumbing ----------
def get_client():
    """
    Reuse your existing order client factory (Angel One / stub).
    Env: USE_STUB=true uses in-memory data.
    """
    use_stub = str(os.getenv("USE_STUB", "true")).lower() == "true"
    if use_stub:
        return _StubClient()
    # live path — adapt to your factory/session names
    from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
    from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory
    sess = AngelOneSession.from_env()
    # create accepts "smart_connect" OR "angelone" (see UI patch below)
    return OrderClientFactory.create("smart_connect", sess)

# ---------- endpoints ----------
@router.get("/chain", response_model=ChainResp)
def chain(
    underlying: str = Query(..., description="Underlying symbol, e.g., NIFTY"),
    expirySel: ExpirySel = Query(...),
    expiry: Optional[str] = Query(None, description="YYYY-MM-DD when expirySel=custom"),
    client = Depends(get_client),
):
    rows = client.option_chain(underlying=underlying, expirySel=expirySel, expiry=expiry)
    if not rows:
        raise HTTPException(404, "No option chain found")
    return ChainResp(underlying=underlying, expiry=rows[0]["expiry"], rows=[ChainRow(**r) for r in rows])

@router.post("/resolve", response_model=ResolveResp)
def resolve(req: ResolveReq, client = Depends(get_client)):
    ts, ex = client.resolve_option(
        underlying=req.underlying,
        side=req.side,
        strikeSel=req.strikeSel,
        steps=req.steps,
        strike=req.strike,
        expirySel=req.expirySel,
        expiry=req.expiry,
    )
    return ResolveResp(tradingsymbol=ts, exchange=ex)

@router.get("/value", response_model=ValueResp)
def value(symbol: str, field: Literal["ltp","iv","oi"], client = Depends(get_client)):
    v = client.option_value(symbol, field)
    return ValueResp(symbol=symbol, field=field, value=float(v), ts=int(time.time()*1000))

@router.get("/greeks", response_model=GreekResp)
def greeks(symbol: str, client = Depends(get_client)):
    g = client.greeks(symbol)
    return GreekResp(symbol=symbol, **g, ts=int(time.time()*1000))

# ---------- stub client (so UI can integrate immediately) ----------
class _StubClient:
    def option_chain(self, underlying: str, expirySel: str, expiry: Optional[str]):
        # tiny fake chain over 3 strikes (ATM±1) for demo
        base = 22500
        exdate = expiry or "2025-09-04"
        def row(strike, side, ltp, iv, oi):
            return dict(
                tradingsymbol=f"{underlying}{exdate.replace('-','')[2:]}{int(strike)}{side}",
                exchange="NFO", strike=float(strike), side=side, expiry=exdate,
                ltp=float(ltp), iv=float(iv), oi=int(oi), bid=ltp-0.2, ask=ltp+0.2
            )
        return [
            row(base-100, "CE", 110.0, 12.3, 350000),
            row(base,     "CE", 220.0, 11.8, 420000),
            row(base+100, "CE", 115.0, 12.0, 300000),
            row(base-100, "PE", 115.0, 12.1, 330000),
            row(base,     "PE", 230.0, 11.9, 410000),
            row(base+100, "PE", 120.0, 12.2, 310000),
        ]

    def resolve_option(self, **kw) -> tuple[str,str]:
        # naive resolver for demo: pick ATM or ±steps x 100
        chain = self.option_chain(kw["underlying"], kw["expirySel"], kw.get("expiry"))
        strikes = sorted({r["strike"] for r in chain})
        atm = strikes[len(strikes)//2]
        strike = atm
        if kw["strikeSel"] == "OTM+steps":
            step = (kw.get("steps") or 0) * 100
            strike = atm + step if kw["side"] == "CE" else atm - step
        elif kw["strikeSel"] == "ITM+steps":
            step = (kw.get("steps") or 0) * 100
            strike = atm - step if kw["side"] == "CE" else atm + step
        elif kw["strikeSel"] == "ByStrike":
            strike = float(kw.get("strike") or atm)
        # find first matching row
        for r in chain:
            if r["strike"] == strike and r["side"] == kw["side"]:
                return r["tradingsymbol"], r["exchange"]
        return chain[0]["tradingsymbol"], chain[0]["exchange"]

    def option_value(self, symbol: str, field: str) -> float:
        # derive from fake symbol just to return something stable
        h = abs(hash(symbol)) % 1000
        if field == "ltp": return 100 + (h % 200) / 10
        if field == "iv":  return 10 + (h % 50) / 10
        if field == "oi":  return 300000 + (h % 100000)
        raise ValueError("field must be ltp|iv|oi")

    def greeks(self, symbol: str) -> Dict[str, float]:
        h = abs(hash(symbol)) % 100
        return dict(delta=0.5 - (h%10)/100, gamma=0.01 + (h%5)/1000, theta=-0.1 - (h%7)/100, vega=0.2 + (h%9)/100)
