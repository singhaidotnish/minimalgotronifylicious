>  _“See [INSTALL.md](INSTALL.md) for setup instructions.”_
> 
> > > 1️⃣ Market Data Arrives → SmartWebSocketV2Client receives live data from the broker's WebSocket.
> 2️⃣ Notifying Backend Observers → The backend observers (e.g., database, email) process the data.
> 3️⃣ Notifying Frontend Clients →

> WebSocketObserver in FastAPI sends live data to all connected WebSocket clients (frontend).
> The frontend (e.g., Next.js) updates charts in real-time.


        +------------------+      +-------------------------+
        |  Trading API     |      |  SmartWebSocketV2Client |
        |  (Broker Feed)   | ---> |  (Market Data Source)  |
        +------------------+      +-------------------------+
                                           ⬇
        +--------------------------------------------------+
        |  Backend (Python)                               |
        |  - DatabaseObserver (Store data)               |
        |  - EmailObserver (Send alerts)                 |
        |  - StrategyObserver (Apply trade strategies)   |
        |  - WebSocketObserver (Send to WebSocket)       |
        +--------------------------------------------------+
                                           ⬇
        +--------------------------------------------------+
        |  FastAPI WebSocket Server (Exposes /ws route)   |
        +--------------------------------------------------+
                                           ⬇
        +---------------------------+
        |  Frontend (Next.js, React)|
        |  - Connects to WebSocket  |
        |  - Displays live charts   |
        +---------------------------+


# algomin
> pip installation
> cd algomin/base
> pip install -e .
> cd algomin/live
> pip install -e .
> pip install SmartApi websocket-client pandas matplotlib plotly


#### ✅ python -m unittest tests/test_session
#### ✅ python -m unittest tests/test_candle_data
#### ✅ python -m unittest tests/test_smartwebsocket
#### ✅ python -m unittest tests/test_smartwebsocket
#### ✅ python -m  live.lusing_smartwebsocketv2
#### ✅ python -m  live.order_with_derivative_or_stock.py
#### ~~python3 -m tests.test_candle_data > results/test_candle_data_results.txt~~




> Get current data. Also,
> * For a ONE_DAY interval , current data becomes history after 3:30 pm of current day
> * For a ONE_MINUTE interval, current data becomes history after a minute and likewise for ONE_HOUR and so on
> * All history is uploaded to database on cloud
> * * So Find a cloud which allows to host database for free
> * * What does work, docker and database as a microservice


##### Observer Pattern for live data

>   WebSocketObserver defines an interface for all observers.
    LoggerObserver logs every received message.
    AlertObserver triggers an alert if a certain price threshold is exceeded.


>   Manages WebSocket connection.
    Maintains a list of observers.
    Notifies observers whenever a message is received.

>   Runs ws.run_forever() inside a separate thread, allowing the main program to remain responsive.

##### Run the script

###### This implementation makes it easy to add new observers (e.g., a database logger) without modifying the core WebSocket handling logic.
> python -m live.observer_live_api

