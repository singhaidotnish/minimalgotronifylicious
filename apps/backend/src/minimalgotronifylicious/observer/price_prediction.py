import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from collections import deque
import json

from .base_observer import BaseObserver

class PricePredictionObserver(BaseObserver):
    """Observer that uses ML to predict future prices."""
    def __init__(self, lookback=10):
        self.lookback = lookback  # Number of past data points to use
        self.data_queue = deque(maxlen=lookback)  # Store past prices
        self.model = LinearRegression()  # Simple regression model

    def train_model(self):
        """Train ML model using past price data."""
        if len(self.data_queue) < self.lookback:
            return None  # Not enough data to train

        df = pd.DataFrame(self.data_queue, columns=["timestamp", "ltp"])
        df["time_index"] = range(len(df))

        X = df[["time_index"]].values  # Time as input
        y = df["ltp"].values  # LTP as target

        self.model.fit(X, y)  # Train model

    def predict_next_price(self):
        """Predict next price based on ML model."""
        if len(self.data_queue) < self.lookback:
            return None  # Not enough data

        next_time_index = len(self.data_queue)
        return self.model.predict([[next_time_index]])[0]

    def update(self, message):
        """Receives live market data and makes a price prediction."""
        try:
            data = json.loads(message)
            for item in data["data"]:
                timestamp = item["exchange_timestamp"]
                ltp = item.get("ltp", 0)

                self.data_queue.append((timestamp, ltp))  # Store data
                self.train_model()  # Train model

                predicted_price = self.predict_next_price()
                if predicted_price:
                    print(f"📈 Predicted Next Price: {predicted_price:.2f}")

        except Exception as e:
            print(f"⚠️ Error in ML Observer: {e}")
