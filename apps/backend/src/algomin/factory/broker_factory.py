from typing import Any, Type, Dict
from src.algomin.config_loader.broker_config_loader import BrokerConfigLoader
from src.algomin.sessions.angelone_session import AngelOneSession
from src.algomin.sessions.zerodha_session import ZerodhaSession

class BrokerFactory:
    """
    Factory for creating broker sessions. Register new brokers here.
    """
    _registry: Dict[str, Type] = {
        "angel_one": AngelOneSession,
        "zerodha": ZerodhaSession,
    }

    @classmethod
    def create_session(cls, broker: str, config_loader: BrokerConfigLoader) -> Any:
        """
        Instantiate and return a session for the given broker key.

        Raises KeyError if broker is unsupported.
        """
        key = broker.lower()
        if key not in cls._registry:
            raise KeyError(f"Unsupported broker: {broker}")
        # Load broker-specific credentials
        creds = config_loader.load_credentials(key)
        session_class = cls._registry[key]
        return session_class(creds)

    @classmethod
    def register_broker(cls, broker_key: str, session_cls: Type) -> None:
        """
        Register a new broker session class under the given key.
        """
        cls._registry[broker_key.lower()] = session_cls
