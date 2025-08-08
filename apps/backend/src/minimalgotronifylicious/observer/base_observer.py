# Observer Interface
class BaseObserver:
    def update(self, message):
        raise NotImplementedError("Observer must implement the update method.")
