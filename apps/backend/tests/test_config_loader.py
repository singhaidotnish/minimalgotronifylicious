import yaml
import pytest

from src.algomin.config_loader import BrokerConfigLoader

@pytest.fixture(autouse=True)
def fake_config(tmp_path, monkeypatch):
    # Write a fake data/config.yaml
    cfg = {
        "credentials": {"user": "u", "pass": "p"},
        "websocket": {"foo": "bar"},
    }
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    cfg_file = data_dir / "config.yaml"
    cfg_file.write_text(yaml.safe_dump(cfg))
    # Point the loader to our temp config
    monkeypatch.setattr(
        BrokerConfigLoader, "CONFIG_PATH", cfg_file
    )
    return cfg

def test_load_credentials(fake_config):
    loader = BrokerConfigLoader()
    assert loader.load_credentials() == fake_config["credentials"]

def test_load_websocket_config(fake_config):
    loader = BrokerConfigLoader()
    assert loader.load_websocket_config() == fake_config["websocket"]

def test_missing_file(tmp_path):
    # Point to a non-existent file
    bad_path = tmp_path / "nope.yaml"
    from src.algomin.config_loader.broker_config_loader import BrokerConfigLoader
    monkey = pytest.MonkeyPatch()
    monkey.setattr(BrokerConfigLoader, "CONFIG_PATH", bad_path)
    loader = BrokerConfigLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_credentials()
    monkey.undo()
