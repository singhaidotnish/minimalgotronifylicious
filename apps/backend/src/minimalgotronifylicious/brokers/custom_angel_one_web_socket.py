from SmartApi.smartWebSocketV2 import SmartWebSocketV2


class CustomAngelOneWebSocketV2(SmartWebSocketV2):
    def __init__(
        self,
        auth_token,
        api_key,
        client_id,
        feed_token,
        max_retry_attempt=3,
        retry_strategy=1,
        retry_delay=5,
        retry_multiplier=2,
        retry_duration=30
    ):
        super().__init__(auth_token, api_key, client_id, feed_token)
        self._connected = False
        self.on_open = self._on_open
        self.on_close = self._on_close_wrapper
        self.on_error = self._on_error
        # Your custom retry params or additional setup
        self.max_retry_attempt = max_retry_attempt
        self.retry_strategy = retry_strategy
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.retry_duration = retry_duration

    def _on_open(self, wsapp):
        self._connected = True
        print("WebSocket connected")

    def _on_close_wrapper(self, ws, close_status_code, close_msg):
        # Call the class-defined 2-param method
        print(f"WebSocket closed with code {close_status_code}, message: {close_msg}")
        self._on_close(ws)

    def _on_close(self, wsapp):
        # Optional: Handle or log closure
        self._connected = False
        print("WebSocket closed")

    def _on_error(self, wsapp, error):
        self._connected = False
        print(f"WebSocket error: {error}")

    def is_connected(self):
        return self._connected