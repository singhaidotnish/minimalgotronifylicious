# brokers/abstract_websocket_client.py
from src.algomin.brokers.base_websocket_client import BaseWebSocketClient


class AbstractWebSocketClient(BaseWebSocketClient):
    def __init__(self):
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def _on_open(self, wsapp):
        self._connected = True
        print(f"{self.__class__.__name__} connected")

    def _on_close(self, wsapp):
        self._connected = False
        print(f"{self.__class__.__name__} disconnected")

    def _on_error(self, wsapp, error):
        self._connected = False
        print(f"{self.__class__.__name__} error: {error}")

    def _on_control_message(self, wsapp, message):
        print(f"{self.__class__.__name__} control message: {message}")

    def set_callbacks(self, on_data, on_open=None, on_close=None, on_error=None, on_control_message=None):
        # Allow clients to override or default to internal handlers
        self._on_data = on_data
        self._on_open = on_open or self._on_open
        self._on_close = on_close or self._on_close
        self._on_error = on_error or self._on_error
        self._on_control_message = on_control_message or self._on_control_message

    def disconnect(self):
        raise NotImplementedError(f"{self.__class__.__name__}.disconnect() must be implemented by subclass")

    def subscribe(self, correlation_id: str, mode: str, token_list: list):
        raise NotImplementedError(f"{self.__class__.__name__}.subscribe() must be implemented by subclass")

    def run_forever(self):
        raise NotImplementedError(f"{self.__class__.__name__}.run_forever() must be implemented by subclass")
