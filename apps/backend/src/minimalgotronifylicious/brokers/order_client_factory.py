from __future__ import annotations
from typing import Optional, Any
import os

from src.minimalgotronifylicious.utils.broker_registry import (
    load_registry, defaults, paper_env_enabled,
    make_client_from_registry,
)

def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower().replace("-", "_")

def resolve_broker_name(broker: Optional[str], market_open: Optional[bool]) -> str:
    reg = load_registry()
    wanted = _norm(broker or os.getenv("BROKER", "auto"))

    # env kill-switch for CI/dev
    if paper_env_enabled() and wanted not in ("angel_one","binance"):
        wanted = "paper_trade"

    if wanted == "auto":
        d = defaults()
        wanted = _norm(d.get("when_auto_open" if market_open else "when_auto_closed", "paper_trade"))

    if wanted not in reg:
        raise ValueError(f"Unsupported broker: {wanted}")
    return wanted

def order_client_factory(
    broker: Optional[str] = None,
    *,
    session: Any = None,
    market_open: Optional[bool] = None
):
    name = resolve_broker_name(broker, market_open)

    # Angel One sanity check for lives
    if name == "angel_one":
        required = ["SMARTAPI_API_KEY","SMARTAPI_CLIENT_CODE","SMARTAPI_TOTP_SECRET"]
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            raise RuntimeError(f"Missing env: {', '.join(missing)}")

    return make_client_from_registry(name, session=session)

# Back-compat exports
def make_client(broker: Optional[str] = None, *, session=None, market_open: Optional[bool] = None):
    return order_client_factory(broker, session=session, market_open=market_open)

class OrderClientFactory:
    @staticmethod
    def create(broker: Optional[str] = None, session=None, market_open: Optional[bool] = None):
        return order_client_factory(broker, session=session, market_open=market_open)

__all__ = ["order_client_factory", "make_client", "OrderClientFactory", "resolve_broker_name"]
