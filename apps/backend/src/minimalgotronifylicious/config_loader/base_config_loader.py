# config/base_config_loader.py
from abc import ABC, abstractmethod

class BaseConfigLoader(ABC):
    @abstractmethod
    def load_credentials(self) -> dict: pass

    @abstractmethod
    def load_websocket_config(self) -> dict: pass
