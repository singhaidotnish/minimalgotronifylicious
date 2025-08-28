from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory

auth_data = {
    "client_id": "P123456",
    "api_key": "abcd123",
    "password": "1234",
    "totp": "BASE32SECRET"
}

client = OrderClientFactory.create("angel_one", auth_data)

order = {
    "variety": "NORMAL",
    "tradingsymbol": "SBIN-EQ",
    "symboltoken": "3045",
    "transactiontype": "BUY",
    "exchange": "NSE",
    "ordertype": "LIMIT",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "price": "19500",
    "squareoff": "0",
    "stoploss": "0",
    "quantity": "1"
}

response = client.place_order(order)
print(response)
