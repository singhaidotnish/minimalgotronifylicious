# src/minimalgotronifylicious/brokers/order_client_factory.py
from __future__ import annotations
from dataclasses import dataclass
import os
CANONICAL = "angel_one"

@dataclass
class OrderClientFactory:
    @staticmethod
    def create(broker: str, session):
        # PAPER/DEMO path first
        if os.getenv("PAPER_TRADING", "true").strip().lower() == "true":
            from src.minimalgotronifylicious.brokers.paper_client import PaperClient
            seed = float(os.getenv("DEMO_SEED_CASH", "100000"))
            return PaperClient(seed_cash=seed)

        key = (broker or "").lower().replace("-", "_")
        if key != CANONICAL:
            raise ValueError(f"Unsupported broker: {broker} (use '{CANONICAL}')")
        # Lazy import avoids circular imports and boot-time crashes
        from src.minimalgotronifylicious.brokers.angelone_angel_one_client import AngelOneConnectClient
        return AngelOneConnectClient(session)

# Back-compat for existing code/tests
def order_client_factory(broker: str, session):
    return OrderClientFactory.create(broker, session)

make_client = order_client_factory

__all__ = ["OrderClientFactory", "order_client_factory", "make_client"]
