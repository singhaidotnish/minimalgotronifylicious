import pandas as pd
import datetime
from collections import deque
import plotly.graph_objects as go
from .base_observer import BaseObserver


class ChartObserver(BaseObserver):
    def __init__(self, window_size=50):
        self.data_queue = deque(maxlen=window_size)
        self.fig = go.Figure()

    def update(self, data):
        for item in data.get("data", []):
            timestamp = datetime.datetime.now()  # or use real timestamp
            ltp = item.get("ltp", 0) / 100
            self.data_queue.append({"timestamp": timestamp, "ltp": ltp})

    def render_chart(self):
        df = pd.DataFrame(self.data_queue)
        if not df.empty:
            self.fig.data = []  # Clear previous
            self.fig.add_trace(go.Scatter(x=df["timestamp"], y=df["ltp"], mode="lines", name="LTP"))
            self.fig.update_layout(title="Live Price", xaxis_title="Time", yaxis_title="Price")
            self.fig.show()

