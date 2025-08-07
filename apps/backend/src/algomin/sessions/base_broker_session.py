# sessions/base_session.py
from abc import ABC, abstractmethod
from typing import Any


class BaseBrokerSession(ABC):

    @abstractmethod
    def login(self) -> None:
        """
        Perform authentication or session initialization steps.
        """
        pass

    @abstractmethod
    def get_auth_info(self) -> dict:
        pass

    @abstractmethod
    def fetch_candles(
        self,
        symbol: str,
        interval: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
        limit: int | None = None,
        **extra_params: Any
    ) -> Any:
        """
        Fetch historical candlestick data for a given symbol and interval.

        Args:
            symbol: Trading symbol identifier.
            interval: Timeframe for each candle (e.g., 'ONE_MINUTE').
            from_ts: Optional start timestamp in milliseconds.
            to_ts: Optional end timestamp in milliseconds.
            limit: Optional maximum number of candles to retrieve.
            **extra_params: Additional broker-specific parameters.

        Returns:
            Raw candle data as provided by the broker API.
        """
        pass
