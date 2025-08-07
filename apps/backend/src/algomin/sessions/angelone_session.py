import pyotp
from logzero import logger
from SmartApi import SmartConnect
from typing import Any, Dict, Optional
from src.algomin.sessions.base_broker_session import BaseBrokerSession  # your abstract base


class AngelOneSession(BaseBrokerSession):
    def __init__(self, credentials):
        self.api_key = credentials["api_key"]
        self.client_id = credentials["client_id"]
        self.password = credentials["password"]
        _totp_secret = credentials["totp_secret"]
        self.totp = pyotp.TOTP(_totp_secret).now()
        self.api = SmartConnect(api_key=self.api_key)

        self.auth_token = None
        self.feed_token = None
        self.refresh_token = None
        self.login()

    def login(self):
        data = self.api.generateSession(self.client_id, self.password, self.totp)
        if data['status'] == False:
            logger.error(data)
        else:
            # logger.info(f"+++ data: {data}")
            self.auth_token = data["data"]["jwtToken"]
            self.refresh_token = data['data']['refreshToken']
            self.feed_token = self.api.getfeedToken()
            # logger.info(f" +++ from api Feed-Token :{self.feed_token}")
            res = self.api.getProfile(self.refresh_token)
            # logger.info(f"+++ from api Get Profile: {res}")

            self.api.generateToken(self.refresh_token)
            res=res['data']['exchanges']
            # logger.info(f"+++ from api res data exchanges : {res}")


    def get_auth_info(self):
        return {
            "auth_token": self.auth_token,
            "feed_token": self.feed_token,
            "refresh_token": self.refresh_token,
            "api_key": self.api_key,
            "client_id": self.client_id
        }

    def fetch_candles(
        self,
        symbol: str,
        interval: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        limit: Optional[int] = None,
        **extra_params: Any
    ) -> Any:
        """
        Fetch historical candlestick data via AngelOne’s REST API.
        Delegates to SmartConnect’s getCandleData under the hood.
        """
        # Map our unified args to SmartConnect fields
        params: Dict[str, Any] = {
            "symboltoken": symbol,
            "interval": interval,
        }
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts
        if limit is not None:
            params["limit"] = limit

        # Attach any broker-specific extras
        params.update(extra_params)

        # Perform the request
        resp = self.api.getCandleData(**params)
        # Optionally: validate/normalize resp here before returning
        return resp