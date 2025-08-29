from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException

from typing import Optional
from pydantic import BaseModel
from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory
from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession
from src.minimalgotronifylicious.config_loader.broker_config_loader import BrokerConfigLoader
from src.minimalgotronifylicious.utils.order_builder import OrderBuilder

from src.minimalgotronifylicious.web_socket_manager import WebSocketManager
from src.minimalgotronifylicious.brokers.websocket_client_factory import WebSocketClientFactory
from src.minimalgotronifylicious.api.brokers import router as brokers_router
from src.minimalgotronifylicious.routers import angel_one
from src.minimalgotronifylicious.routers.angel_one import router as angel_router

import apps.backend.src.minimalgotronifylicious.routers.trading

router = APIRouter()
router.include_router(brokers_router)
router.include_router(angel_router)

class OrderRequest(BaseModel):
    tradingsymbol: str
    symboltoken: str
    transactiontype: str
    exchange: str
    ordertype: str
    quantity: int
    price: str = "0"
    squareoff: str = "0"
    stoploss: str = "0"
    producttype: str = "INTRADAY"
    duration: str = "DAY"
    variety: str = "NORMAL"
    is_exit: bool = False
    trailing_sl: bool = False


@router.get("/")
def root():
    return {"status": "ok"}


@router.post("/order/place")
def place_order(order: OrderRequest):
    builder = OrderBuilder(order.dict())
    valid, reason = builder.validate()
    if not valid:
        return {"status": "error", "reason": reason}

    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    session = AngelOneSession(credentials)
    client = OrderClientFactory.create("angel_one", session)

    clean_order = builder.build()
    return apps.backend.src.minimalgotronifylicious.routers.trading.place_order(clean_order)

@router.get("/candles")
def get_candles(
    symbol: str = Query(..., description="Trading symbol, e.g. NIFTY21JUL6700CE"),
    interval: str = Query(..., description="Candle interval, e.g. ‘ONE_MINUTE’, ‘FIVE_MINUTE’, etc."),
    from_ts: Optional[int] = Query(None, alias="from", description="Unix timestamp (milliseconds) for start"),
    to_ts:   Optional[int] = Query(None, alias="to",   description="Unix timestamp (milliseconds) for end"),
    limit:   Optional[int] = Query(None, description="Max number of bars to return"),
    **extra_params  # will capture any other query params you tack on
    ):
    """
    Fetch historical candlestick data from AngelOne.
    """
    # --- initialize session ---
    config_loader = BrokerConfigLoader()
    creds = config_loader.load_credentials()
    session = AngelOneSession(creds)

    # --- prepare upstream params ---
    params = {
        "symboltoken": symbol,
        "interval": interval,
    }
    if from_ts is not None:
        params["from"] = from_ts
    if to_ts is not None:
        params["to"] = to_ts
    if limit is not None:
        params["limit"] = limit
    # include any additional filters
    params.update(extra_params)

    try:
        # SmartConnect’s method for fetching candles is typically named `getCandleData`
        resp = session.api.getCandleData(**params)
    except Exception as e:
        # Bubble up a 502 if AngelOne is unhappy
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    # `resp` should already be JSON-serializable (list of [time, open, high, low, close, volume] arrays)
    return resp


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/ping")
def ping():
    return {"status": "ok", "message": "minimalgotronifylicious backend is live"}


@router.get("/ws/stream")
async def ws_stream_info():
    return {"info": "This endpoint only speaks WebSocket — use a WS client."}


@router.websocket("/ws/stream")
async def stream_data(websocket: WebSocket, broker: str = "angel_one"):
    await websocket.accept()

    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    session = AngelOneSession(credentials)  # in future, use broker condition

    ws_config = config_loader.load_websocket_config()
    ws_config["session"] = session

    client = WebSocketClientFactory.create(broker, ws_config)
    ws_manager = WebSocketManager(client)
    ws_manager.start()

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            symbol = data.get("symbol")

            if action == "subscribe":
                ws_manager.register(symbol, websocket)
            elif action == "unsubscribe":
                ws_manager.unregister(symbol, websocket)
    except WebSocketDisconnect:
        ws_manager.unregister_all(websocket)
