# brokers/base_event_handler.py

from abc import ABC, abstractmethod

class BaseEventHandler(ABC):
    @abstractmethod
    def on_data(self, ws, message): pass

    @abstractmethod
    def on_open(self, ws): pass

    @abstractmethod
    def on_close(self, ws): pass

    @abstractmethod
    def on_error(self, ws, error): pass
