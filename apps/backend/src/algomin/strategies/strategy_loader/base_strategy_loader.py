# strategy_loader/base_strategy_loader.py
from abc import ABC, abstractmethod

class BaseStrategyLoader(ABC):
    @abstractmethod
    def load_strategies(self, path: str) -> list:
        pass
