from base.session import Session

# fetch market data for stock

class Order:
    def __init__(self):
        self.session_obj = Session()

    def fetch_market_data_for_stock(self, tradingsymbol="RELIANCE", symboltoken="2885"):
        stock_params = {
            "exchange": "NSE",
            "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken
        }

        data = self.session_obj.smart_api.ltpData(**stock_params)
        print("LTP Data:", data)

    # market order for stock
    def market_order_for_stock(self, type="BUY"):
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": "RELIANCE",
            "symboltoken": "2885",
            "transactiontype": type,  # Use "SELL" for selling
            "exchange": "NSE",
            "ordertype": "MARKET",
            "producttype": "INTRADAY",  # or "DELIVERY" for long-term
            "duration": "DAY",
            "quantity": 1
        }

        order_response = self.session_obj.smart_api.placeOrder(order_params)
        print("Order Response:", order_response)

    # buy / sell derivatives
    def transact_derivatives(self):
        option_order = {
            "variety": "NORMAL",
            "tradingsymbol": "NIFTY24FEB18000CE",
            "symboltoken": "123456",  # Get token from contract files
            "transactiontype": "BUY",
            "exchange": "NFO",
            "ordertype": "LIMIT",
            "price": 50,  # Set price for limit order
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": 50  # Options trade in lots, check lot size
        }

        order_response = self.session_obj.smart_api.placeOrder(option_order)
        print("Option Order Response:", order_response)

        # fetch order status
        order_id = order_response["data"]["orderid"]
        order_status = self.session_obj.smart_api.orderBook()
        print("Order Status:", order_status)
        return order_id

    def cancel(self, order_id):
        # cancel order
        cancel_response = self.session_obj.smart_api.cancelOrder(order_id=order_id)
        print("Cancel Order Response:", cancel_response)
