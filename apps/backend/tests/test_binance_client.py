import os
from src.minimalgotronifylicious.brokers.binance_client import BinanceClient

import apps.backend.src.minimalgotronifylicious.routers.trading


def test_stub_ltp():
    os.environ["USE_PAPER"] = "true"
    c = BinanceClient()
    p = c.ltp("BINANCE:BTCUSDT")
    assert isinstance(p, float)

def test_stub_order_market():
    os.environ["USE_PAPER"] = "true"
    c = BinanceClient()
    resp = apps.backend.src.minimalgotronifylicious.routers.trading.place_order("BINANCE:BTCUSDT", "BUY", 0.001, "MARKET")
    assert resp["status"] == "ACCEPTED"
