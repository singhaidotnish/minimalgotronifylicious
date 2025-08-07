from src.algomin.sessions.angelone_session import AngelOneSession
from src.algomin.config_loader import BrokerConfigLoader
from src.algomin.brokers.angelone_websocket_client import AngelOneWebSocketV2Client
from src.algomin.brokers.angelone_websocket_event_handler import AngelOneWebSocketEventHandler

# Step 1: Load config
config_loader = BrokerConfigLoader()
credentials = config_loader.load_credentials()
# get credentials for AngelOne and what instrument needs live data
ws_config = config_loader.load_websocket_config()

# Step 2: Optionally load strategies (skip for live tick test)
strategies = []

# Step 3: Start session
session = AngelOneSession(credentials)

# Step 6: Init WebSocket client
retry_config = ws_config.get("retry", {})
ws_client = AngelOneWebSocketV2Client(
    session,
    max_retry_attempt=retry_config.get("max_attempt", 3),
    retry_strategy=retry_config.get("strategy", 1),
    retry_delay=retry_config.get("delay", 5),
    retry_multiplier=retry_config.get("multiplier", 2),
    retry_duration=retry_config.get("duration", 30)
)
# Step 7: Init event handler
event_handler = AngelOneWebSocketEventHandler(
    strategy_executor=None,
    correlation_id=ws_config.get("correlation_id", "sub_default"),
    mode=ws_config.get("mode", "full"),
    token_list=ws_config.get("subscriptions", []),
    sws=ws_client.sws
)

# Step 8: Attach callbacks
ws_client.set_callbacks(
    event_handler.on_data,
    event_handler.on_open,
    event_handler.on_close,
    event_handler.on_error,
    event_handler.on_control_message
)

# Step 9: Connect and wait for ticks
ws_client.connect()

if hasattr(ws_client, "add_observer"):
    ws_client.add_observer(event_handler)

if hasattr(ws_client, "start_heartbeat"):
    ws_client.start_heartbeat()

ws_client.run_forever()
# ws_client.sws._ws.run_forever()