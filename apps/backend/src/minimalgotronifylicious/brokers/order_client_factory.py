from __future__ import annotations
from typing import Optional, Any
import os

from src.minimalgotronifylicious.utils.broker_registry import (
    load_registry, defaults, paper_env_enabled,
    make_client_from_registry,
)

# src/minimalgotronifylicious/brokers/order_client_factory.py (or wherever it lives)

from typing import Optional
import os
from src.minimalgotronifylicious.utils.broker_registry import load_registry, paper_env_enabled

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _alias(name: str) -> str:
    # map common spellings to your registry key "angel_one"
    aliases = {
        "angelone": "angel_one",
        "angel-one": "angel_one",
        "angel": "angel_one",
        "smartconnect": "angel_one",
        "smart_connect": "angel_one",
        # add more if needed
    }
    return aliases.get(_norm(name), _norm(name))

def defaults():
    # from your brokers.yaml defaults
    return {"when_auto_open": "angel_one", "when_auto_closed": "paper_trade"}

def resolve_broker_name(broker: Optional[str], market_open: Optional[bool]) -> str:
    reg = load_registry()
    wanted = _alias(broker) or _alias(os.getenv("BROKER", "auto"))

    # CI/dev paper guard
    if paper_env_enabled() and wanted not in ("angel_one", "binance", "paper_trade", "auto"):
        wanted = "paper_trade"

    if wanted == "auto":
        d = defaults()
        wanted = _alias(d["when_auto_open" if market_open else "when_auto_closed"])

    wanted = _alias(wanted)
    if wanted not in reg:
        raise ValueError(f"Unsupported broker: {wanted}")
    return wanted

def order_client_factory(
    broker: Optional[str] = None,
    *,
    session=None,
    market_open: Optional[bool] = None
):
    name = resolve_broker_name(broker, market_open)

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

# src/minimalgotronifylicious/brokers/order_client_factory.py
class OrderClientFactory:
    @staticmethod
    def create(broker_name: str, session):
        name = (broker_name or "").lower()
        if name in ("smart_connect", "angelone", "angel-one"):
            return AngelOneConnectClient(session)
        raise ValueError(f"Unsupported broker: {broker_name}")
