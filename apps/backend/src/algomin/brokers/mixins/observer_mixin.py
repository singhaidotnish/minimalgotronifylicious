# brokers/mixins/observer_mixin.py

class ObserverMixin:
    def __init__(self):
        # { symbol: [observer1, observer2, ...] }
        self.observers = {}

    def add_observer(self, symbol, observer):
        if symbol not in self.observers:
            self.observers[symbol] = []
        self.observers[symbol].append(observer)

    def remove_observer(self, symbol, observer):
        if symbol in self.observers:
            self.observers[symbol] = [obs for obs in self.observers[symbol] if obs != observer]
            if not self.observers[symbol]:
                del self.observers[symbol]

    def remove_all_for_observer(self, observer):
        for symbol in list(self.observers.keys()):
            self.observers[symbol] = [obs for obs in self.observers[symbol] if obs != observer]
            if not self.observers[symbol]:
                del self.observers[symbol]

    def notify_observers(self, symbol, data):
        if symbol in self.observers:
            for obs in self.observers[symbol]:
                obs.update(data)
