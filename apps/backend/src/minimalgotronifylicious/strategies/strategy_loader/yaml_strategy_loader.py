# yaml_strategy_loader.py
import yaml
from src.minimalgotronifylicious.strategies.strategy_loader.base_strategy_loader import BaseStrategyLoader

class YAMLStrategyLoader(BaseStrategyLoader):
    def load_strategies(self, path: str) -> list:
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            return data.get("limit_order_strategies", [])
        except Exception as e:
            print(f"⚠️ Failed to load strategy YAML: {e}")
            return []
