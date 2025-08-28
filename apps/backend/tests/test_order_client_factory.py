# tests/test_order_client_factory.py
import importlib, os

def test_factory_export_and_stub(monkeypatch):
    # Run CI in stub mode (no real creds required)
    monkeypatch.setenv("PAPER_TRADING", "true")
    m = importlib.import_module("src.minimalgotronifylicious.brokers.order_client_factory")
    assert hasattr(m, "order_client_factory") or hasattr(m, "make_client")

    # If you have a StubClient, ensure the DI decides correctly
    from src.minimalgotronifylicious.routers import angel_one
    c = angel_one.get_client()
    price = c.ltp("NSE:SBIN-EQ")
    assert isinstance(price, (int, float))
