# apps/backend/src/minimalgotronifylicious/deps/broker.py
from fastapi import Header, HTTPException
from typing import Optional
import os
from src.minimalgotronifylicious.brokers.order_client_factory import order_client_factory

def client_dep(
    x_broker: Optional[str] = Header(None, convert_underscores=False),
    x_market_open: Optional[str] = Header(None, convert_underscores=False),
):
    broker = (x_broker or os.getenv("BROKER", "auto")).strip().lower().replace("-", "_")
    market_open = (x_market_open or "").strip().lower() in ("1","true","yes","on")

    try:
        if broker == "angel_one":
            # session is the only special case
            from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
            sess = AngelOneSession.from_env()
            return order_client_factory("angel_one", session=sess)
        return order_client_factory(broker, market_open=market_open)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
