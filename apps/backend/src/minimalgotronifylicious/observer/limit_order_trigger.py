from .base_observer import BaseObserver
from core.session import AngelOneSession

class LimitOrderTriggerObserver(BaseObserver):
    def __init__(self, tradingsymbol, target_price, quantity, symbol_token, order_type="BUY"):
        self.tradingsymbol = tradingsymbol
        self.target_price = target_price
        self.quantity = quantity
        self.symbol_token = symbol_token
        self.triggered = False
        self.order_type = order_type  # "BUY" or "SELL"
        self.session = AngelOneSession()

    def update(self, market_data):
        ltp = market_data["ltp"]
        if not self.triggered and ltp <= self.target_price:
            print(f"📌 LTP dropped to {ltp}, placing limit order at {self.target_price}")
            self.place_limit_order()
            self.triggered = True

    def place_limit_order(self):
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": self.tradingsymbol,  # Example: adjust to your symbol
            "symboltoken": self.symbol_token,
            "transactiontype": self.order_type,
            "exchange": "NSE",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": self.target_price,
            "quantity": self.quantity
        }
        try:
            smart_api = self.session.get_api()
            response = smart_api.placeOrder(order_params)
            print("✅ Order response:", response)
        except Exception as e:
            print(f"❌ Failed to place order: {e}")
