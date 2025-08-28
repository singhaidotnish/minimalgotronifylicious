class StubClient:
    def ltp(self, symbol: str): return 123.45
    def place_order(self, **kwargs): return {"status": "ACCEPTED", **kwargs}
