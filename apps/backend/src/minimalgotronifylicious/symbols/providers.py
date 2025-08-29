from __future__ import annotations
import os, json
from typing import List, Dict

# Tiny helpers to allow cached files during dev; replace with API calls later.

def _json(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def nse_provider() -> List[Dict]:
    """
    Source of truth for NSE instruments.
    Prefer a cached JSON path via NSE_SYMBOLS_PATH (generated offline),
    then fall back to a tiny hardcoded seed list.
    """
    p = os.getenv("NSE_SYMBOLS_PATH")
    if p and os.path.exists(p):
        return _json(p)
    # seed list; replace after you wire your NSE loader
    return [
        {"symbol": "NSE:SBIN-EQ", "label": "SBIN", "kind": "equity"},
        # options here only if you want; better to let UI filter by kind
        # {"symbol":"NFO:BANKNIFTY25SEP45000CE", "label":"BANKNIFTY 25-Sep 45000 CE", "kind":"option"},
    ]

def binance_provider():
    """
    Prefer cached exchangeInfo JSON from BINANCE_SYMBOLS_PATH.
    Transform -> [{symbol, label, kind}]
    """
    p = os.getenv("BINANCE_SYMBOLS_PATH")
    if not p or not os.path.exists(p):
        # tiny safe seed to keep picker working
        return [
            {"symbol": "BINANCE:BTCUSDT", "label": "BTC/USDT", "kind": "crypto_spot"},
            {"symbol": "BINANCE:ETHUSDT", "label": "ETH/USDT", "kind": "crypto_spot"},
        ]
    data = _json(p)
    items = []
    for s in data.get("symbols", []):
        if s.get("status") != "TRADING":
            continue
        sym = s.get("symbol")
        base = s.get("baseAsset")
        quote = s.get("quoteAsset")
        # Keep it simple: USDT spot pairs look great in UI; adjust as you like
        label = f"{base}/{quote}"
        items.append({"symbol": f"BINANCE:{sym}", "label": label, "kind": "crypto_spot"})
    return items


def paper_provider() -> List[Dict]:
    # paper can aggregate a few to keep the picker useful
    return [
        {"symbol": "BINANCE:BTCUSDT", "label": "BTC/USDT", "kind": "crypto_spot"},
        {"symbol": "NSE:SBIN-EQ", "label": "SBIN", "kind": "equity"},
    ]
