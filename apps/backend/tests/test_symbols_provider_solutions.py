def test_symbols_provider_resolution(monkeypatch):
    from src.minimalgotronifylicious.utils.broker_registry import get_symbols_provider
    # should not blow up for known keys
    for name in ("angel_one","binance","paper_trade"):
        provider = get_symbols_provider(name)
        items = provider()
        assert isinstance(items, list)
