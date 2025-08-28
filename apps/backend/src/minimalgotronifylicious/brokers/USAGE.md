```
USAGE
from brokers.websocket_factory import WebSocketClientFactory

auth_data = {
    "auth_token": "...",
    "feed_token": "...",
    "api_key": "...",
    "client_id": "..."
}

client = WebSocketClientFactory.create("angel_one", auth_data)

# Setup event handlers
client.set_callbacks(
    on_data=my_on_data_handler,
    on_open=my_on_open,
    on_close=my_on_close,
    on_error=my_on_error
)

client.connect()
client.subscribe("sub_123", "full", [{"exchangeType": 1, "tokens": ["7", "14366"]}])
client.run_forever()
```