# orders/base_order_strategy.py

from abc import ABC, abstractmethod

class BaseOrderStrategy(ABC):
    @abstractmethod
    def build_order_params(self, strategy_config: dict) -> dict:
        pass

