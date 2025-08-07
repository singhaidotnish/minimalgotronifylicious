import pyotp
from logzero import logger
from SmartApi import SmartConnect
from typing import Any, Dict, Optional
from src.algomin.sessions.base_broker_session import BaseBrokerSession  # your abstract base


class ZerodhaSession(BaseBrokerSession):
    def __init__(self, credentials):
        pass

    def login(self):
        pass

    def get_auth_info(self):
        pass

    def fetch_candles(
        self,
        symbol: str,
        interval: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        limit: Optional[int] = None,
        **extra_params: Any
    ) -> Any:
        pass