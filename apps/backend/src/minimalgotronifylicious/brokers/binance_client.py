import os, time, hmac, hashlib, requests, math
from typing import Optional, Dict, Any
from .interfaces import IOrderClient, OrderType, Side

# Toggle testnet easily
_BASE_SPOT = "https://api.binance.com"
_BASE_FUT  = "https://fapi.binance.com"
_BASE_SPOT_TEST = "https://testnet.binance.vision"
_BASE_FUT_TEST  = "https://testnet.binancefuture.com"  # fallback; some test envs vary

def _now_ms() -> int:
    return int(time.time() * 1000)

class BinanceClient(IOrderClient):
    """
    Minimal adapter for Binance (spot or futures).
    - Symbols we accept: "BINANCE:BTCUSDT" (best) or "BTCUSDT" (we'll normalize)
    - ENV:
        BINANCE_API_KEY, BINANCE_API_SECRET (optional if STUB=true)
        BINANCE_USE_FUTURES=true|false
        BINANCE_TESTNET=true|false
        USE_STUB=true|false  (shared flag in your app)
    """
    def __init__(self, session: Optional[object] = None) -> None:
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        self.use_futures = os.getenv("BINANCE_USE_FUTURES", "false").lower() == "true"
        self.testnet = os.getenv("BINANCE_TESTNET", "false").lower() == "true"
        self.stub = os.getenv("USE_STUB", "true").lower() == "true"

        if self.use_futures:
            self.base = _BASE_FUT_TEST if self.testnet else _BASE_FUT
        else:
            self.base = _BASE_SPOT_TEST if self.testnet else _BASE_SPOT

        self.sess = requests.Session()
        if self.api_key:
            self.sess.headers.update({"X-MBX-APIKEY": self.api_key})

    # ---------- helpers ----------
    def _sym(self, s: str) -> str:
        # Accept "BINANCE:BTCUSDT" or "BTCUSDT"
        return s.split(":", 1)[1] if ":" in s else s

    def _sign_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params = dict(params)
        params["timestamp"] = _now_ms()
        q = "&".join(f"{k}={params[k]}" for k in sorted(params.keys()))
        sig = hmac.new(self.api_secret.encode(), q.encode(), hashlib.sha256).hexdigest()
        params["signature"] = sig
        return params

    def _get(self, path: str, params: Dict[str, Any] = None, signed: bool = False):
        params = params or {}
        if signed:
            params = self._sign_params(params)
        r = self.sess.get(self.base + path, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, params: Dict[str, Any] = None, signed: bool = False):
        params = params or {}
        if signed:
            params = self._sign_params(params)
        r = self.sess.post(self.base + path, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    # ---------- interface ----------
    def login(self) -> None:
        # Binance is key+sig; nothing to do. Keep parity with other brokers.
        if self.stub:
            return
        if not (self.api_key and self.api_secret):
            raise RuntimeError("BINANCE_API_KEY / BINANCE_API_SECRET missing")

    def logout(self) -> None:
        # no-op
        return

    def ltp(self, symbol: str, *, exchange: Optional[str] = None) -> float:
        # Futures `/ticker/price` & spot `/ticker/price` are same shape
        if self.stub:
            # deterministic fake price so graphs don't jump wildly
            s = self._sym(symbol)
            base = sum(ord(ch) for ch in s) % 1000
            return round(100 + base + (time.time() % 1), 2)

        sym = self._sym(symbol)
        data = self._get("/fapi/v1/ticker/price" if self.use_futures else "/api/v3/ticker/price",
                         {"symbol": sym})
        return float(data["price"])

    def place_order(
        self,
        symbol: str,
        side: Side,
        qty: float,
        order_type: OrderType,
        price: Optional[float] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        if self.stub:
            return {
                "orderId": f"stub-{int(time.time()*1000)}",
                "status": "ACCEPTED",
                "message": "stubbed",
            }

        sym = self._sym(symbol)
        side_u = side.upper()
        type_u = order_type.upper()

        params = {
            "symbol": sym,
            "side": side_u,
            "type": type_u,
            "quantity": qty,
            # Binance accepts different fields depending on MARKET vs LIMIT
            # For LIMIT we must pass timeInForce + price
        }
        if type_u == "LIMIT":
            if price is None:
                raise ValueError("price required for LIMIT")
            params["timeInForce"] = "GTC"
            # Round price to a sensible tick if caller didn't
            params["price"] = price

        path = "/fapi/v1/order" if self.use_futures else "/api/v3/order"
        return self._post(path, params, signed=True)

    def positions(self) -> Dict[str, Any]:
        if self.stub:
            return {"ok": True, "positions": []}

        if self.use_futures:
            # Futures account positions
            data = self._get("/fapi/v2/positionRisk", signed=True)
            # Normalize a tiny bit
            return {"ok": True, "positions": data}
        else:
            # Spot has balances, not leveraged positions; return non-zero assets as "positions"
            acct = self._get("/api/v3/account", signed=True)
            positions = [a for a in acct.get("balances", []) if float(a["free"]) + float(a["locked"]) > 0]
            return {"ok": True, "positions": positions}
