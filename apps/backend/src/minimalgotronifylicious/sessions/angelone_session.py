# src/minimalgotronifylicious/sessions/angelone_session.py
from __future__ import annotations
import os
from logzero import logger
from SmartApi import SmartConnect
from dataclasses import dataclass
from typing import Any, Dict, Optional
from src.minimalgotronifylicious.sessions.base_broker_session import BaseBrokerSession  # your abstract base
from src.minimalgotronifylicious.utils.net import get_public_ip

# Optional base; keep compatibility if you already have it
try:
    from src.minimalgotronifylicious.sessions.base_broker_session import BaseBrokerSession  # type: ignore
except Exception:  # fallback so imports never break
    class BaseBrokerSession:  # type: ignore
        pass


# ---------- Credentials container ----------
@dataclass
class AngelOneCreds:
    api_key: str
    client_id: str
    password: str
    totp_secret: str
    pan: Optional[str] = None

    @classmethod
    def from_env(cls) -> "AngelOneCreds":
        """
        Reads SMARTAPI_* environment variables and returns a creds object.
        Required:
          SMARTAPI_API_KEY, SMARTAPI_CLIENT_ID, SMARTAPI_PASSWORD, SMARTAPI_TOTP_SECRET
        Optional:
          SMARTAPI_PAN
        """
        required = [
            "SMARTAPI_API_KEY",
            "SMARTAPI_CLIENT_ID",
            "SMARTAPI_PASSWORD",
            "SMARTAPI_TOTP_SECRET",
        ]
        vals = {k: os.getenv(k, "").strip() for k in required}
        missing = [k for k, v in vals.items() if not v]
        if missing:
            raise RuntimeError(f"Missing env for AngelOne: {', '.join(missing)}")

        pan = os.getenv("SMARTAPI_PAN", "").strip() or None
        return cls(
            api_key=vals["SMARTAPI_API_KEY"],
            client_id=vals["SMARTAPI_CLIENT_ID"],
            password=vals["SMARTAPI_PASSWORD"],
            totp_secret=vals["SMARTAPI_TOTP_SECRET"],
            pan=pan,
        )


# ---------- Session ----------
class AngelOneSession(BaseBrokerSession):
    """
    Thin wrapper around SmartApi SmartConnect with a simple login flow.
    Keeps the old method names for backwards compatibility (login, get_auth_info, fetch_candles).
    """

    def __init__(self, credentials: AngelOneCreds):
        self.creds = credentials

        # Will be set by login()
        self.api = None                 # SmartConnect instance
        self.auth_token: Optional[str] = None
        self.feed_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

        self.public_ip: Optional[str] = None
        self.default_headers: Dict[str, str] = {}

    # ---- Factory helpers ----
    @classmethod
    def from_env(cls) -> "AngelOneSession":
        """
        Reads env, performs login, returns a ready session.
        """
        creds = AngelOneCreds.from_env()
        sess = cls(creds)
        sess.login()
        return sess

    # Optional: if you still want YAML support
    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "AngelOneSession":
        creds = AngelOneCreds(
            api_key=cfg["api_key"],
            client_id=cfg["client_id"],
            password=cfg["password"],
            totp_secret=cfg["totp_secret"],
            pan=cfg.get("pan"),
        )
        sess = cls(creds)
        sess.login()
        return sess

    # ---- Live login & tokens ----
    def login(self) -> None:
        """
        Performs SmartApi login. Lazy-imports heavy deps to avoid breaking demo mode imports.
        """
        try:
            # Lazy imports so module import doesn't fail in USE_PAPER mode
            import pyotp  # type: ignore
            from SmartApi import SmartConnect  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "Required packages for AngelOne live session are missing. "
                "Install pyotp and smartapi-python (Angel One SmartAPI) to use live mode."
            ) from e

        totp_now = pyotp.TOTP(self.creds.totp_secret).now()
        self.api = SmartConnect(api_key=self.creds.api_key)

        data = self.api.generateSession(self.creds.client_id, self.creds.password, totp_now)
        if not data or data.get("status") is False:
            logger.error({"where": "angelone.login.generateSession", "resp": data})
            raise RuntimeError(f"AngelOne login failed: {data}")

        d = data["data"]
        self.auth_token = d["jwtToken"]
        self.refresh_token = d["refreshToken"]
        self.feed_token = self.api.getfeedToken()

        # Optional best-effort calls
        try:
            _ = self.api.getProfile(self.refresh_token)
            self.api.generateToken(self.refresh_token)
        except Exception as e:
            logger.debug(f"AngelOne post-login extras failed (non-fatal): {e}")

        # Public IP & default headers (best-effort)
        try:
            from src.minimalgotronifylicious.utils.net import get_public_ip
            self.public_ip = get_public_ip()
            self.default_headers = {
                "X-Forwarded-For": self.public_ip,
                "X-Client-IP": self.public_ip,
            }
        except Exception as e:
            logger.debug(f"Could not resolve public IP (non-fatal): {e}")

    # ---- Compatibility helpers ----
    def get_auth_info(self) -> Dict[str, Any]:
        return {
            "auth_token": self.auth_token,
            "feed_token": self.feed_token,
            "refresh_token": self.refresh_token,
            "api_key": self.creds.api_key,
            "client_id": self.creds.client_id,
        }

    # ---- Example data method ----
    def fetch_candles(
        self,
        symbol: str,
        interval: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        limit: Optional[int] = None,
        **extra_params: Any,
    ) -> Any:
        """
        Fetch historical candlestick data via SmartConnect.getCandleData.
        Maps our unified args to SmartConnect fields.
        """
        if not self.api:
            raise RuntimeError("AngelOne session not initialized (self.api is None). Did you call login()?")

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
        params.update(extra_params)

        return self.api.getCandleData(**params)
