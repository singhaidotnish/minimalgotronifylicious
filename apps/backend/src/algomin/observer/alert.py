from .base_observer import BaseObserver


class AlertObserver(BaseObserver):
    def update(self, data):
        ltp = data["ltp"]
        ema = data["ema"]

        # Define conditions for sending alerts
        if ltp < ema and data.get("prev_close", ema) > ema:
            print("[ALERT] LTP below EMA, closing above EMA - Consider SELL.")
            # Call email function here

        elif ltp > ema and data.get("prev_close", ema) < ema:
            print("[ALERT] LTP above EMA, closing below EMA - Consider PUT.")
            # Call email function here


