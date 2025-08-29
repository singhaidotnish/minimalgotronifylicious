# tests/test_registry_factory.py
import os
from src.minimalgotronifylicious.brokers.order_client_factory import resolve_broker_name, order_client_factory

def test_auto_closed_is_paper():
    os.environ["USE_PAPER"] = "false"
    assert resolve_broker_name("auto", False) == "paper_trade"

def test_auto_open_is_live():
    os.environ["USE_PAPER"] = "false"
    assert resolve_broker_name("auto", True) == "angel_one"

def test_factory_paper_instance():
    c = order_client_factory("paper_trade")
    assert hasattr(c, "positions")
