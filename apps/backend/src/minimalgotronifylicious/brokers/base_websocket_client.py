# brokers/base_websocket_client.py
from abc import ABC, abstractmethod

class BaseWebSocketClient(ABC):
    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def disconnect(self): pass

    @abstractmethod
    def is_connected(self) -> bool: pass

    @abstractmethod
    def subscribe(self, correlation_id: str, mode: str, token_list: list): pass

    @abstractmethod
    def set_callbacks(self, on_data, on_open, on_close, on_error, on_control_message): pass

    @abstractmethod
    def run_forever(self): pass
