from abc import ABC, abstractmethod

class DataLoader(ABC):
    @abstractmethod
    def load(self) -> dict:
        pass
