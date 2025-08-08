from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
from src.minimalgotronifylicious.config_loader import BrokerConfigLoader
from src.minimalgotronifylicious.brokers.angelone_websocket_event_handler import AngelOneWebSocketEventHandler

from src.minimalgotronifylicious.brokers.websocket_client_factory import WebSocketClientFactory
from src.minimalgotronifylicious.web_socket_manager import WebSocketManager


def main():
    print("🚀 Starting WebSocket Live Data Test for AngelOne")

    # Step 1: Load credentials and websocket config
    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    ws_config = config_loader.load_websocket_config()

    # Step 2: Start AngelOne session
    session = AngelOneSession(credentials)
    ws_config["session"] = session

    # Step 3: Create broker-agnostic WebSocket client
    client = WebSocketClientFactory.create("angel_one", ws_config)

    # Step 4: Initialize manager to control client lifecycle
    ws_manager = WebSocketManager(client)

    # Step 5: Prepare event handler to process live ticks
    event_handler = AngelOneWebSocketEventHandler(
        strategy_executor=None,  # can be hooked later
        correlation_id=ws_config.get("correlation_id", "sub_default"),
        mode=ws_config.get("mode", "full"),
        token_list=ws_config.get("subscriptions", []),
        sws=ws_manager.ws_client.sws
    )

    # Step 6: Register callbacks before starting the connection
    ws_manager.ws_client.set_callbacks(
        event_handler.on_data,
        event_handler.on_open,
        event_handler.on_close,
        event_handler.on_error,
        event_handler.on_control_message
    )

    # Step 7: Start the WebSocket manager (handles connect + watchdog)
    ws_manager.start()

    # Keep the script running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n🛑 Interrupted. Stopping WebSocket...")
        ws_manager.stop()

if __name__ == "__main__":
    main()
