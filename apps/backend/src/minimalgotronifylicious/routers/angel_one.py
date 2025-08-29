# src/minimalgotronifylicious/routers/angel_one.py
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Header, Body
from pydantic import BaseModel, Field

from src.minimalgotronifylicious.brokers.order_client_factory import resolve_broker_name, order_client_factory
from src.minimalgotronifylicious.symbols.service import list_for

router = APIRouter(prefix="/api/angel_one", tags=["angel-one"])

# ---------------------------
# Routes
# ---------------------------

@router.get("/ltp")
def deprecated_ltp_redirect():
    # short, loud, and action-guiding
    raise HTTPException(
        status_code=410,
        detail="Deprecated: use GET /api/ltp?symbol=..."
    )
