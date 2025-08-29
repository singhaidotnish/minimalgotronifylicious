# src/minimalgotronifylicious/symbols/service.py
import os, json
from typing import List, Dict

def _from_json(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_for(broker: str) -> List[Dict]:
    """
    Return [{symbol, label, kind}] lightweight list for the picker.
    Overridable via env files for quick experiments.
    """
    # Optional external lists:
    if broker == "binance" and (p := os.getenv("BINANCE_SYMBOLS_PATH")):
        return _from_json(p)
    if broker == "angel_one" and (p := os.getenv("NSE_SYMBOLS_PATH")):
        return _from_json(p)

    # Defaults (safe, small):
    if broker == "binance":
        return [
            {"symbol": "BINANCE:BTCUSDT", "label": "BTC/USDT", "kind": "crypto_spot"},
            {"symbol": "BINANCE:ETHUSDT", "label": "ETH/USDT", "kind": "crypto_spot"},
        ]
    if broker == "angel_one":
        return [
            {"symbol": "NSE:SBIN-EQ", "label": "SBIN", "kind": "equity"},
            {"symbol": "NSE:RELIANCE-EQ", "label": "RELIANCE", "kind": "equity"},
            # examples for options (UI can hide if broker says no)
            {"symbol": "NFO:BANKNIFTY25SEP45000CE", "label": "BANKNIFTY 25-Sep 45000 CE", "kind": "option"},
        ]
    # Paper inherits a generic mix
    return [
        {"symbol": "BINANCE:BTCUSDT", "label": "BTC/USDT", "kind": "crypto_spot"},
        {"symbol": "NSE:SBIN-EQ", "label": "SBIN", "kind": "equity"},
    ]
