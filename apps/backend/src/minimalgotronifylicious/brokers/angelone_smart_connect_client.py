# brokers/smart_trading_client.py
from logzero import logger

from src.minimalgotronifylicious.brokers.abstract_trading_client import AbstractOrderClient


class AngelOneConnectClient(AbstractOrderClient):
    def __init__(self, session):
        self.api = session.api

    def place_order(self, order_data: dict) -> dict:
        try:
            order_id = self.api.placeOrder(order_data)
            logger.info(f"AngelOne SDK response: {order_id}")
            return {"status": "success", "orderid": order_id}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Place order failed: {error_msg}")

            if "market is closed" in error_msg.lower():
                return {
                    "status": "error",
                    "reason": "Market is closed. Order cannot be placed outside market hours.",
                    "input": order_data
                }

            return {"status": "error", "error": error_msg, "input": order_data}


    def cancel_order(self, order_id: str):
        return self.api.cancelOrder({"orderid": order_id})

    def modify_order(self, order_id: str, updated_data: dict) -> dict:
        try:
            params = {
                "orderid": order_id,
                "tradingsymbol": updated_data["tradingsymbol"],
                "exchange": updated_data["exchange"],
                "ordertype": updated_data["ordertype"],
                "producttype": updated_data.get("producttype", "INTRADAY"),
                "duration": updated_data.get("duration", "DAY"),
                "price": updated_data.get("price", "0"),
                "quantity": updated_data["quantity"]
            }

            # For SL/SL-M order types
            if params["ordertype"] in {"SL", "SL-M"}:
                params["triggerprice"] = updated_data["triggerprice"]

            response = self.api.modifyOrder(params)
            return {
                "status": "success",
                "orderid": response.get("data", {}).get("orderid", order_id),
                "message": "Order modified"
            }
        except Exception as e:
            logger.error(f"Modify order failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "input": updated_data
            }

    def get_positions(self):
        return self.api.position()

    def get_holdings(self):
        return self.api.holdings()

    def get_order_book(self) -> list:
        raise NotImplementedError("Order book not implemented")

    def get_trade_book(self) -> list:
        raise NotImplementedError("Trade book not implemented")

