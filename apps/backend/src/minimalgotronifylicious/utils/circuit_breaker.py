import time

class Circuit:
    def __init__(self, threshold=5, reset_ms=30_000):
        self.failures = 0
        self.open_until = 0
        self.threshold = threshold
        self.reset_ms = reset_ms

    def open(self) -> bool:
        return time.time() * 1000 < self.open_until

    def fail(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.open_until = int(time.time() * 1000) + self.reset_ms
            self.failures = 0

    def ok(self):
        self.failures = 0
