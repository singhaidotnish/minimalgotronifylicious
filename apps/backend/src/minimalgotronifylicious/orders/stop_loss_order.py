# orders/stop_loss_order.py

from src.minimalgotronifylicious.orders.base_order_strategy import BaseOrderStrategy

class StopLossOrderStrategy(BaseOrderStrategy):
    def build_order_params(self, strategy_config):
        return {
            "variety": "NORMAL",
            "tradingsymbol": strategy_config["tradingsymbol"],
            "symboltoken": strategy_config["symbol_token"],
            "transactiontype": strategy_config["order_type"],
            "exchange": "NSE",
            "ordertype": "SL",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": strategy_config["target_price"],
            "triggerprice": strategy_config["trigger_price"],
            "quantity": strategy_config["quantity"]
        }
