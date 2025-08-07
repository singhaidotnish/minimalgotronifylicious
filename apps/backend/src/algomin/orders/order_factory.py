# orders/order_factory.py

from src.algomin.orders.limit_order import LimitOrderStrategy
from src.algomin.orders.market_order import MarketOrderStrategy
from src.algomin.orders.stop_loss_order import StopLossOrderStrategy

class OrderFactory:
    @staticmethod
    def get_order_strategy(order_type: str):
        if order_type == "LIMIT":
            return LimitOrderStrategy()
        elif order_type == "MARKET":
            return MarketOrderStrategy()
        elif order_type == "SL":
            return StopLossOrderStrategy()
        else:
            raise ValueError(f"Unsupported order type: {order_type}")
