import time
import threading

from src.minimalgotronifylicious.brokers.abstract_websocket_client import AbstractWebSocketClient
from src.minimalgotronifylicious.brokers.mixins.observer_mixin import ObserverMixin
from src.minimalgotronifylicious.brokers.custom_angel_one_web_socket import CustomAngelOneWebSocketV2

class AngelOneWebSocketV2Client(AbstractWebSocketClient, ObserverMixin):
    def __init__(self,
                 session,
                 max_retry_attempt,
                 retry_strategy,
                 retry_delay,
                 retry_multiplier,
                 retry_duration
                 ):
        super().__init__()
        ObserverMixin.__init__(self)
        self.session = session
        auth_info = self.session.get_auth_info()
        self.max_retry_attempt = max_retry_attempt
        self.retry_strategy = retry_strategy
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.retry_duration = retry_duration


        self.auth_token = auth_info["auth_token"]
        self.feed_token = auth_info["feed_token"]
        self.api_key = auth_info["api_key"]
        self.client_id = auth_info["client_id"]

        self.sws = CustomAngelOneWebSocketV2(
            self.auth_token,
            self.api_key,
            self.client_id,
            self.feed_token,
            self.max_retry_attempt,
            self.retry_strategy,
            self.retry_delay,
            self.retry_multiplier,
            self.retry_duration
        )
        self.lock = threading.Lock()
        self.correlation_id = f"subscription_{int(time.time())}"
        self.mode = "full"
        self.token_list = []

    def set_callbacks(self, on_data, on_open=None, on_close=None, on_error=None, on_control_message=None):
        self.sws.on_data = on_data
        self.sws.on_open = on_open
        self.sws.on_close = on_close
        self.sws.on_error = on_error
        self.sws.on_control_message = on_control_message

        # NEW: Add observer if available
        # if hasattr(self, "add_observer") and callable(getattr(self, "add_observer", None)):
        #     self.add_observer(on_data)  # or pass event_handler if needed
        # Observer registration is handled via WebSocketManager.register()

        # NEW: Start heartbeat if supported
        # if hasattr(self.sws, "start_heartbeat"):
        #     self.sws.start_heartbeat()

        # if not getattr(self, "_heartbeat_started", False):
        #     self.sws.start_heartbeat()
        #     self._heartbeat_started = True

    def connect(self):
        self.sws.connect()

    def subscribe(self, correlation_id: str, mode: str, token_list: list):
        self.correlation_id = correlation_id
        self.mode = mode
        self.token_list = token_list
        print(f'+++ subscribe to : {token_list}')
        self.sws.subscribe(
            correlation_id=self.correlation_id,
            mode=self.mode,
            token_list=self.token_list
        )

    def run_forever(self):
        if self.sws and self.sws._ws:
            self.sws._ws.run_forever()

    def is_connected(self) -> bool:
        return self.sws.is_connected()

    def disconnect(self):
        self.sws.close_connection()
