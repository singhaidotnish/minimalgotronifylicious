from fastapi.testclient import TestClient
import pytest
import asyncio
import datetime
import pytz
import os

from main import app

client = TestClient(app)

# Define market hours in IST
IST = pytz.timezone("Asia/Kolkata")
MARKET_OPEN = datetime.time(9, 15)
MARKET_CLOSE = datetime.time(15, 30)


def is_market_open():
    # CI override to force fake stream
    if os.getenv("FORCE_FAKE_STREAM", "").lower() == "true":
        return False

    now = datetime.datetime.now(IST)
    return (
        now.weekday() < 5  # Monday=0, Sunday=6
        and MARKET_OPEN <= now.time() <= MARKET_CLOSE
    )


def test_root_status():
    response = client.get("/")
    assert response.status_code == 200
    # Root serves HTML index page
    html = response.text
    assert "<!DOCTYPE html>" in html
    assert "<div id=\"root\"></div>" in html


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ping_endpoint():
    response = client.get("/ping")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "ok"
    assert "algomin backend is live" in payload.get("message", "")


def test_ws_stream_info():
    response = client.get("/ws/stream")
    assert response.status_code == 200
    assert response.json() == {"info": "This endpoint only speaks WebSocket — use a WS client."}


def test_ws_stream_connection(monkeypatch):
    """
    Test WebSocket /ws/stream endpoint by mocking the event source to push a test message.
    Fake data only when market is closed; skips real stream during open hours.
    """
    if is_market_open():
        pytest.skip("Market is open; skipping fake data override to allow real data stream")

    # Dummy event generator
    from src.algomin.api.routes import stream_events  # adjust import to actual generator

    test_message = {"symbol": "TESTSYM", "price": 123.45}

    async def dummy_generator():
        yield test_message
        await asyncio.sleep(0)

    # Override the generator
    monkeypatch.setattr(
        "src.algomin.api.routes.stream_events", lambda: dummy_generator()
    )

    with client.websocket_connect("/ws/stream") as ws:
        data = ws.receive_json(timeout=1)
        assert data == test_message
        ws.close()

@pytest.mark.skip(reason="Requires external broker/session. Integration test to be implemented with mocks")
def test_place_order_integration():
    payload = {
        "tradingsymbol": "TESTSYM",
        "symboltoken": "12345",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "quantity": 1
    }
    response = client.post("/order/place", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") in {"success", "error"}

# To make the frontend live chart work, ensure WebSocket emits real-time tick data.
