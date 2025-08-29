from fastapi.testclient import TestClient
from src.minimalgotronifylicious.app import app


def test_routes_unique():
    seen = set()
    for r in app.routes:
        if getattr(r, "path", None) and getattr(r, "methods", None):
            for m in r.methods:
                key = (m, r.path)
                assert key not in seen, f"Duplicate route {m} {r.path}"
                seen.add(key)

def test_symbols_ok(client: TestClient):
    res = client.get("/api/symbols", headers={"X-Broker":"auto","X-Market-Open":"false"})
    assert res.status_code == 200
    assert "items" in res.json()

def test_ltp_ok(client: TestClient):
    res = client.get("/api/ltp", params={"symbol":"BINANCE:BTCUSDT"},
                     headers={"X-Broker":"binance"})
    assert res.status_code == 200
