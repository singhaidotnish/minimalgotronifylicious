# tests/test_factory_registry.py
import os
from src.minimalgotronifylicious.brokers.order_client_factory import order_client_factory

def test_auto_resolves_to_paper_when_closed():
    os.environ["USE_PAPER"] = "false"
    c = order_client_factory("auto", market_open=False)
    assert hasattr(c, "positions")

def test_paper_force_from_env():
    os.environ["USE_PAPER"] = "true"
    c = order_client_factory("auto", market_open=True)  # would be live, but env forces paper
    assert hasattr(c, "positions")
