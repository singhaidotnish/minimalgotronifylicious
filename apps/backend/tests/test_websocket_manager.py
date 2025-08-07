from unittest.mock import MagicMock
from src.algomin.web_socket_manager import WebSocketManager

def test_watchdog_reconnects_on_disconnect():
    fake_client = MagicMock()
    fake_client.is_connected.side_effect = [False, True]  # first call False, then True

    manager = WebSocketManager(fake_client, heartbeat_interval=0.1)
    manager.start()

    # Let it run a short while
    import time
    time.sleep(0.2)

    assert fake_client.connect.called
    manager.stop()
