from .base_loader import DataLoader

class DatabaseLoader(DataLoader):
    def __init__(self, db_session):
        self.db_session = db_session

    def load(self) -> dict:
        return self.db_session.query_strategies()  # Your actual DB call


"""
Use -:
loader = DatabaseLoader(my_db_session)
strategies = loader.load()

"""