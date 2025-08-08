# command : python -m live.bracket_order_derivative_stock

from base.session import Session
import yaml
import os
from pathlib import Path

"""
    Pattern Type : Factory Pattern
    Description : If you want to dynamically call a class based on a parameter, 
    the Factory Design Pattern is the best approach. This pattern allows 
    selecting the appropriate class at runtime.
    
    The Factory Pattern is useful when you need to create objects dynamically based on 
    runtime parameters. If you have two or more parameters to decide at runtime, you 
    can implement a factory method that takes multiple arguments and returns the 
    appropriate instance.    
"""

from abc import ABC, abstractmethod

class LoadConf(ABC):
    def __init__(self, config=None, config_file=None):
        self.current_session = Session()
        if config:
            self.config = config
        elif config_file:
            self.config = self._load_config_from_file(config_file)
        else:
            raise ValueError("Must provide either config dict or config_file")

    def _load_config_from_file(self, file_name):
        _package_dir = Path(__file__).resolve().parent.parent
        config_file = os.path.join(_package_dir, "data", file_name)
        with open(config_file, "r") as file:
            yaml_data = yaml.safe_load(file)
        return self._flatten(yaml_data)

    def _flatten(self, d, parent_key="", sep="."):
        result = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                result.update(self._flatten(v, new_key, sep=sep))
            else:
                result[new_key] = v
        return result

    @abstractmethod
    def execute(self):
        pass

    def verify_login(self):
        # Step 1: Fetch User Profile to verify login
        _client_id = self.current_session.smart_api.cnf.CLIENT_ID
        profile = self.current_session.smart_api.getProfile(_client_id)
        return profile


class MarketOrder(LoadConf):
    def execute(self):
        return "Executing Market Order"


class LimitOrder(LoadConf):
    def execute(self):
        return "Executing Limit Order"


class StopLossOrder(LoadConf):
    def execute(self):
        return "Executing Stop Loss Order"


class BracketOrderStock(LoadConf):
    def execute(self):
        print(f"Executing {self.__class__} with config {self.config_file}")
        order_params = self.load_config()
        print(f"bracket order params :  {order_params}")
        # order_response = self.current_session.smart_api.placeOrder(order_params)
        # return order_response


class BracketOrderDerivative(LoadConf):
    def execute(self):
        print(f"Executing {self.__class__} Order with config {self.config_file}")
        order_params = self.load_config()
        print(f"derivative order params : {order_params}")
        # order_response = self.current_session.smart_api.placeOrder(order_params)
        # return order_response


class OrderFactory:
    @staticmethod
    def create_order(order_type, conf_type):
        orders = {
            "market": MarketOrder,
            "limit": LimitOrder,
            "stop_loss": StopLossOrder,
            "bostock": BracketOrderStock,
            "boderivative": BracketOrderDerivative
        }

        if order_type.lower() in orders:
            return orders[order_type.lower()](conf_type)
        else:
            raise ValueError(f"Unknown order type: {order_type}")


if __name__ == "__main__":
    order_type = input("Enter Order type (bostock/boderivative/market/Limit/StopLoss): ").strip().lower()
    conf_type = input("Enter config type (bo_stock_data.yaml/bo_derivative_data.yaml): ").strip().lower()
    print('+++ order type : ', order_type)
    print('+++ conf type : ', conf_type)
    try:
        order = OrderFactory.create_order(order_type, conf_type)
        print(order.execute())
    except ValueError as e:
        print(e)
