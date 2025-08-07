# config_loader.py
import os
import yaml
from pathlib import Path
from src.algomin.config_loader.base_config_loader import BaseConfigLoader

class BrokerConfigLoader(BaseConfigLoader):
    def __init__(self, path="config_loader/common.yaml"):
        base_dir = Path(__file__).resolve().parent.parent
        self.config_path = base_dir / path
        self.config = self._load_yaml(self.config_path)

    def _load_yaml(self, path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Failed to load YAML from {path}: {e}")
            return {}

    def load_credentials(self):
        if os.getenv("RAILWAY_ENVIRONMENT"):
            return {
                "api_key": os.environ["API_KEY"],
                "client_id": os.environ["CLIENT_ID"],
                "password": os.environ["PASSWORD"],
                "totp_secret": os.environ["TOTP_SECRET"],
            }
        else:
            return self.config.get("smart_connect", {})

    def load_websocket_config(self) -> dict:
        return self.config.get("websocket", {})

    def load_order_config(self) -> dict:
        return self.config.get("order", {})
