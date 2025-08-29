import os
from typing import List, Dict

class SymbolProvider:
    @staticmethod
    def list_symbols() -> List[Dict]:
        broker = os.getenv("BROKER", "angel_one").lower()
        if broker == "binance":
            # minimal: static list now; later call /exchangeInfo for dynamic load
            return [
                {"symbol": "BINANCE:BTCUSDT", "kind": "spot"},
                {"symbol": "BINANCE:ETHUSDT", "kind": "spot"},
            ]
        # default NSE (you likely already have this)
        return [
            {"symbol": "NSE:SBIN-EQ", "kind": "equity"},
            # {"symbol": "NFO:BANKNIFTY24SEP44000CE", "kind": "option"}, ...
        ]
