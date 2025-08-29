# Brokers share one skinny interface so the rest of the app stays calm.
from typing import Protocol, Literal, Optional, Dict, Any

Side = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT"]

class IOrderClient(Protocol):
    def login(self) -> None: ...
    def logout(self) -> None: ...
    def ltp(self, symbol: str, *, exchange: Optional[str] = None) -> float: ...
    def place_order(
        self,
        symbol: str,
        side: Side,
        qty: float,
        order_type: OrderType,
        price: Optional[float] = None,
        **kwargs: Any
    ) -> Dict[str, Any]: ...
    def positions(self) -> Dict[str, Any]: ...
