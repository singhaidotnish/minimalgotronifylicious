# orders/limit_order.py

from src.minimalgotronifylicious.orders.base_order_strategy import BaseOrderStrategy

class LimitOrderStrategy(BaseOrderStrategy):
    def build_order_params(self, strategy_config):
        return {
            "variety": "NORMAL",
            "tradingsymbol": strategy_config["tradingsymbol"],
            "symboltoken": strategy_config["symbol_token"],
            "transactiontype": strategy_config["order_type"],
            "exchange": "NSE",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": strategy_config["target_price"],
            "quantity": strategy_config["quantity"]
        }
