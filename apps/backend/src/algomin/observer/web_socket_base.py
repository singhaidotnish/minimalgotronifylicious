# system modules
import json

# custom modules
from .base_observer import BaseObserver


class WebSocketRealObserver(BaseObserver):
    def __init__(self, websocket):
        self.websocket = websocket

    async def update(self, data):
        await self.websocket.send(json.dumps(data))  # Send live data to frontend
