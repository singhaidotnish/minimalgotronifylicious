# heartbeat_mixin.py
import threading
import time
import json

class HeartbeatMixin:
    def __init__(self):
        self._stop_heartbeat = False
        self._heartbeat_thread = None

    def start_heartbeat(self):
        if not self._heartbeat_thread:
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self._heartbeat_thread.start()

    def _heartbeat_loop(self):
        while not self._stop_heartbeat:
            try:
                if hasattr(self, 'sws') and self.sws and self.sws.sock and self.sws.sock.connected:
                    self.sws.send(json.dumps({
                        "correlationID": self.correlation_id,
                        "action": 1,
                        "params": {
                            "mode": self.mode,
                            "tokenList": self.token_list
                        }
                    }))
            except Exception as e:
                print(f"⚠️ Heartbeat error: {e}")
            time.sleep(30)

    def stop_heartbeat(self):
        self._stop_heartbeat = True