def test_auto_closed_default(monkeypatch):
    from src.minimalgotronifylicious.utils.broker_registry import load_registry
    from src.minimalgotronifylicious.brokers.order_client_factory import resolve_broker_name
    monkeypatch.setenv("BROKER_REGISTRY_PATH", "src/minimalgotronifylicious/config_loader/brokers.yaml")
    load_registry.cache_clear()
    assert resolve_broker_name("auto", False) in ("paper_trade","binance")  # depending on YAML
