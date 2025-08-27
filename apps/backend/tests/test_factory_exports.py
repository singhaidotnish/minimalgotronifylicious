# tests/test_factory_exports.py
def test_factory_symbol_exists():
    import importlib
    m = importlib.import_module('src.minimalgotronifylicious.brokers.order_client_factory')
    assert any(n in dir(m) for n in ('order_client_factory', 'make_client'))

def test_factory_exports_and_names():
    import importlib
    m = importlib.import_module('src.minimalgotronifylicious.brokers.order_client_factory')
    assert hasattr(m, 'order_client_factory')
    assert hasattr(m, 'make_client')  # alias
