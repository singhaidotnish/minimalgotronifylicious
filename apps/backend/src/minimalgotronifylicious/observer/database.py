# system modules
import sqlite3

# custom modules
from .base_observer import BaseObserver


class DatabaseObserver(BaseObserver):
    def __init__(self, db_path="trading_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ltp REAL,
                ema REAL
            )
        """)
        self.conn.commit()

    def update(self, data):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO market_data (timestamp, ltp, ema) VALUES (?, ?, ?)",
                       (data["timestamp"], data["ltp"], data["ema"]))
        self.conn.commit()
