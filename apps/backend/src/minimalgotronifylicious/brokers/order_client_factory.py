# src/minimalgotronifylicious/brokers/order_client_factory.py
from src.minimalgotronifylicious.brokers.angelone_smart_connect_client import AngelOneConnectClient

# Accept both names so callers don't care about internal naming.
_NAME_MAP = {
    "angelone": "smart_connect",
    "smart_connect": "smart_connect",
    # "zerodha": "zerodha",
}

def order_client_factory(broker: str, session):
    norm = _NAME_MAP.get(str(broker).lower(), str(broker).lower())
    if norm == "smart_connect":
        return AngelOneConnectClient(session)
    # elif norm == "zerodha":
    #     return ZerodhaOrderClient(session)
    raise ValueError(f"Unsupported broker: {broker}")

# Optional: keep a second exported name if some code calls make_client()
make_client = order_client_factory

""" EXAMPLE USAGE

# scripts/ltp_demo.py
import os
from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
from src.minimalgotronifylicious.brokers.order_client_factory import order_client_factory

# env must be set for live: SMARTAPI_API_KEY, SMARTAPI_CLIENT_CODE, SMARTAPI_TOTP_SECRET, SMARTAPI_PAN (if used)
sess = AngelOneSession.from_env()

client = order_client_factory("angelone", session=sess)
client.login()                         # create a live session

symbol = "NSE:SBIN-EQ"
price = client.ltp(symbol)             # or client.ltp(exchange="NSE", symbol="SBIN")
print({"symbol": symbol, "ltp": price})

# place a tiny paper order if your client supports a sandbox
# resp = client.order(symbol="NSE:SBIN-EQ", qty=1, side="BUY", type="MARKET")
# print(resp)

client.logout()


from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
from src.minimalgotronifylicious.brokers.order_client_factory import order_client_factory

sess = AngelOneSession.from_env()
client = order_client_factory("angelone", session=sess)
client.login()

resp = client.order(symbol="NSE:SBIN-EQ", qty=1, side="BUY", type="MARKET")  # price=... for LIMIT
print(resp)

client.logout()


"""