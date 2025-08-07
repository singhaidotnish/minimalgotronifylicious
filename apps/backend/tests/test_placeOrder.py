from logzero import logger
from SmartApi.smartConnect import SmartConnect
from utils.ws_config_loader import ConfigLoader  # adjust import as per your structure
import pyotp
import time


config_loader = ConfigLoader()

api_key = config_loader.get("api.api_key")
client_id = config_loader.get("user.client_id")
pwd = config_loader.get("user.password")
token = config_loader.get("user.totp_secret")
smartApi = SmartConnect(api_key)
print('+++ client id ', client_id, " token ", token)
try:
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = f"limit_order_{int(time.time())}"
data = smartApi.generateSession(client_id, pwd, totp)
if data['status'] == False:
    logger.error(data)
else:
    # logger.info(f"data: {data}")
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    feedToken = smartApi.getfeedToken()
    # logger.info(f"Feed-Token :{feedToken}")
    res = smartApi.getProfile(refreshToken)
    # logger.info(f"Get Profile: {res}")
    smartApi.generateToken(refreshToken)
    res=res['data']['exchanges']

    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "SBIN-EQ",
        "symboltoken": "3045",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "6",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
    }
    # Method 1: Place an order and return the order ID
    orderid = smartApi.placeOrder(orderparams)
    logger.info(f"PlaceOrder : {orderid}")

    orderbook=smartApi.orderBook()
    logger.info(f"Order Book: {orderbook}")

    tradebook=smartApi.tradeBook()
    logger.info(f"Trade Book : {tradebook}")

    rmslimit=smartApi.rmsLimit()
    logger.info(f"RMS Limit : {rmslimit}")

    pos=smartApi.position()
    logger.info(f"Position : {pos}")

    holdings=smartApi.holding()
    logger.info(f"Holdings : {holdings}")

    allholdings=smartApi.allholding()
    logger.info(f"AllHoldings : {allholdings}")
