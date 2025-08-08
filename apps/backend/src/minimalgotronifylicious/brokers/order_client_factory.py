# brokers/order_client_factory.py

from src.minimalgotronifylicious.brokers.angelone_smart_connect_client import AngelOneConnectClient
# from brokers.zerodha_order_client import ZerodhaOrderClient

class OrderClientFactory:
    @staticmethod
    def create(broker_name: str, session):
        if broker_name == "smart_connect":
            return AngelOneConnectClient(session)

        # elif broker_name == "zerodha":
        #     return ZerodhaOrderClient(...)

        else:
            raise ValueError(f"Unsupported broker: {broker_name}")

""" EXAMPLE USAGE
from sessions.angelone_session import AngelOneSession
from config_loader.broker_config_loader import BrokerConfigLoader
from brokers.angelone_websocket_event_handler import AngelOneWebSocketEventHandler

# Step 1: Load credentials and websocket config
config_loader = BrokerConfigLoader()
credentials = config_loader.load_credentials()
ws_config = config_loader.load_websocket_config()

# Step 2: Start AngelOne session
session = AngelOneSession(credentials)

client = OrderClientFactory.create("smart_connect", {session
})

order_response = client.place_order({
    "tradingsymbol": "INFY-EQ",
    "symboltoken": "1594",
    "transactiontype": "BUY",
    "exchange": "NSE",
    "ordertype": "MARKET",
    "producttype": "INTRADAY",
    "quantity": "1"
})

print(order_response)



"""