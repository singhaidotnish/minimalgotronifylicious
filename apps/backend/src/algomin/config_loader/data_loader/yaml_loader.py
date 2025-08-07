import yaml
from .base_loader import DataLoader

class YamlLoader(DataLoader):
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self) -> dict:
        with open(self.filepath, 'r') as file:
            return yaml.safe_load(file)
