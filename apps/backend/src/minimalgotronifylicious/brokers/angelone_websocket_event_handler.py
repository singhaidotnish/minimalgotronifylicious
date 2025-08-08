# brokers/smart_event_handler.py
from logzero import logger
import json

class AngelOneWebSocketEventHandler:
    def __init__(self, strategy_executor=None, correlation_id=None, mode=None, token_list=None, sws=None, ws_manager=None):
        self.strategy_executor = strategy_executor
        self.correlation_id = correlation_id
        self.mode = mode
        self.token_list = token_list
        self.sws = sws
        self.ws_manager = ws_manager  # 👈

    def on_data(self, ws, message):
        logger.info("Ticks: {}".format(message))

        try:
            parsed = json.loads(message)
            symbol = parsed.get("symbol")  # or parsed.get("instrument") depending on structure
            if symbol and self.ws_manager:
                self.ws_manager.stream_tick(symbol, parsed)
        except Exception as e:
            logger.error(f"Failed to parse and stream tick: {e}")

    def on_open(self, ws):
        from logzero import logger
        logger.info("✅ WebSocket Opened")

        some_error_condition = False
        if some_error_condition:
            error_message = "Simulated error"
            if hasattr(ws, 'on_error'):
                ws.on_error("Custom Error Type", error_message)
        else:
            if self.sws and self.correlation_id and self.mode and self.token_list:
                self.sws.subscribe(
                    correlation_id=self.correlation_id,
                    mode=self.mode,
                    token_list=self.token_list
                )

            logger.info(f"📡 Subscribed: {self.token_list}")

    def on_close(self, ws): logger.info("❌ WebSocket Closed")
    def on_error(self, ws, error): print("⚠️ WebSocket Error:", error)
    def on_control_message(self, ws, message): print(f"⚠️ Control Message: {message}")

    def close_connection(self):
        if self.sws:
            self.sws.close_connection()
