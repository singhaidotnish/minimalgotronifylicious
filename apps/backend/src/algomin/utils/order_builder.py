class OrderBuilder:
    def __init__(self, base_order: dict):
        self.order = base_order.copy()

    def validate(self) -> tuple[bool, str]:
        required_keys = ["variety", "transactiontype", "ordertype", "exchange", "tradingsymbol", "symboltoken", "producttype", "duration", "quantity"]
        valid_varieties = {"NORMAL", "STOPLOSS", "ROBO"}
        valid_ordertypes = {"LIMIT", "MARKET", "SL", "SL-M"}
        valid_transactiontypes = {"BUY", "SELL"}
        valid_producttypes = {"INTRADAY", "DELIVERY", "CNC", "MTF"}
        valid_durations = {"DAY", "IOC"}

        for key in required_keys:
            if key not in self.order:
                return False, f"Missing required field: {key}"

        if self.order.get("is_exit"):
            # Minimal validation for exit order
            for key in ["tradingsymbol", "symboltoken", "exchange", "transactiontype", "quantity"]:
                if key not in self.order:
                    return False, f"Exit order missing: {key}"
            return True, "Exit order is valid"

        if self.order["variety"] not in valid_varieties:
            return False, f"Invalid variety: {self.order['variety']}"
        if self.order["ordertype"] not in valid_ordertypes:
            return False, f"Invalid ordertype: {self.order['ordertype']}"
        if self.order["transactiontype"] not in valid_transactiontypes:
            return False, f"Invalid transactiontype: {self.order['transactiontype']}"
        if self.order["producttype"] not in valid_producttypes:
            return False, f"Invalid producttype: {self.order['producttype']}"
        if self.order["duration"] not in valid_durations:
            return False, f"Invalid duration: {self.order['duration']}"

        # SL / SL-M require stoploss
        if self.order["ordertype"] in {"SL", "SL-M"}:
            if float(self.order.get("stoploss", 0)) <= 0:
                return False, "Stoploss must be set for SL or SL-M ordertypes"

        # ROBO orders require stoploss and squareoff
        if self.order["variety"] == "ROBO":
            if float(self.order.get("stoploss", 0)) <= 0 or float(self.order.get("squareoff", 0)) <= 0:
                return False, "ROBO (Bracket) orders must include stoploss and squareoff"

        return True, "Order is valid"

    def build(self) -> dict:
        if self.order.get("is_exit"):
            return {
                "variety": "NORMAL",
                "transactiontype": self.order["transactiontype"],  # usually "SELL"
                "ordertype": "MARKET",
                "exchange": self.order["exchange"],
                "producttype": self.order.get("producttype", "INTRADAY"),
                "tradingsymbol": self.order["tradingsymbol"],
                "symboltoken": self.order["symboltoken"],
                "duration": "DAY",
                "quantity": self.order["quantity"]
            }

        # Remove irrelevant fields based on order type
        final = {
            "variety": self.order["variety"],
            "tradingsymbol": self.order["tradingsymbol"],
            "symboltoken": self.order["symboltoken"],
            "transactiontype": self.order["transactiontype"],
            "exchange": self.order["exchange"],
            "ordertype": self.order["ordertype"],
            "producttype": self.order["producttype"],
            "duration": self.order["duration"],
            "quantity": self.order["quantity"]
        }


        if self.order["ordertype"] in {"LIMIT", "SL", "SL-M"}:
            final["price"] = self.order.get("price", "0")

        if self.order["ordertype"] in {"SL", "SL-M"}:
            final["triggerprice"] = self.order["stoploss"]

        if self.order["variety"] == "ROBO":
            final["squareoff"] = self.order["squareoff"]
            final["stoploss"] = self.order["stoploss"]

        return final

