from .base_observer import BaseObserver

# Logger Observer
class LoggerObserver(BaseObserver):
    def update(self, message):
        print(f"📝 [Logger] {message}")

