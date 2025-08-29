
def test_auto_closed_policy_switch(tmp_path, monkeypatch):
    from src.minimalgotronifylicious.utils.broker_registry import load_registry
    from src.minimalgotronifylicious.brokers.order_client_factory import resolve_broker_name

    y1 = tmp_path/"b1.yaml"
    y1.write_text("defaults: {when_auto_open: angel_one, when_auto_closed: paper_trade}\n")
    y2 = tmp_path/"b2.yaml"
    y2.write_text("defaults: {when_auto_open: angel_one, when_auto_closed: binance}\n")

    # case 1: paper closed
    monkeypatch.setenv("BROKER_REGISTRY_PATH", str(y1))
    monkeypatch.setenv("USE_PAPER", "false")
    load_registry.cache_clear()
    assert resolve_broker_name("auto", False) == "paper_trade"

    # case 2: binance closed
    monkeypatch.setenv("BROKER_REGISTRY_PATH", str(y2))
    load_registry.cache_clear()
    assert resolve_broker_name("auto", False) == "binance"
