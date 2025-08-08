# brokers/base_order_client.py

from abc import ABC, abstractmethod

class AbstractOrderClient(ABC):
    @abstractmethod
    def place_order(self, order_data: dict) -> dict:
        """Place a new order"""
        pass

    @abstractmethod
    def modify_order(self, order_id: str, updated_data: dict) -> dict:
        """Modify an existing order"""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> dict:
        """Cancel an existing order"""
        pass

    @abstractmethod
    def get_order_book(self) -> list:
        """Fetch all active/past orders"""
        pass

    @abstractmethod
    def get_trade_book(self) -> list:
        """Fetch executed trades"""
        pass
