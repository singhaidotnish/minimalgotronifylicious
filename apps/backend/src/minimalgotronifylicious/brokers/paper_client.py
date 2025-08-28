from __future__ import annotations
import uuid, time

class PaperClient:
    def __init__(self, seed_cash: float = 100_000.0):
        self.cash = seed_cash
        self.positions = {}  # {symbol: {"qty": int, "avg": float}}
        self.orders = []

    # brokers/paper_client.py
    def ltp(self, symbol: str) -> float:
        px = 100.0 + (hash(symbol) % 500) / 10
        return round(px, 2)


    def place_order(self, symbol: str, qty: int, side: str, **_):
        price = self.ltp(symbol)["ltp"]
        oid = str(uuid.uuid4())
        ts = int(time.time() * 1000)
        self.orders.append({"order_id": oid, "symbol": symbol, "side": side, "price": price, "qty": qty, "ts": ts})
        # Very simple portfolio math
        p = self.positions.get(symbol, {"qty": 0, "avg": 0.0})
        if side.upper() == "BUY":
            new_qty = p["qty"] + qty
            p["avg"] = (p["avg"] * p["qty"] + price * qty) / max(new_qty, 1)
            p["qty"] = new_qty
            self.cash -= price * qty
        else:
            p["qty"] -= qty
            self.cash += price * qty
            if p["qty"] == 0: p["avg"] = 0.0
        self.positions[symbol] = p
        return {"status": "ACCEPTED", "order_id": oid, "symbol": symbol, "side": side, "price": price, "qty": qty, "ts": ts}

    # convenience for portfolio endpoints
    def snapshot(self):
        m2m = sum(self.ltp(s)["ltp"] * p["qty"] for s, p in self.positions.items())
        return {"cash": round(self.cash, 2), "positions": [{"symbol": s, **p} for s, p in self.positions.items()],
                "market_value": round(m2m, 2), "equity": round(self.cash + m2m, 2)}
