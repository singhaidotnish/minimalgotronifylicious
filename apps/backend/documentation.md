# Algomin & Algomin-UI Documentation Guide

This guide outlines the structure, key concepts, and best practices for both the **algomin** backend and the **algomin-ui** frontend. Use it as the basis for your README files or a full documentation site.

---

## 1. Overview

### 1.1 What is Algomin?  
A modular algorithmic trading toolkit providing:
- Unified broker sessions (`algomin`)
- Real-time and historical market data
- WebSocket & REST interfaces
- Pluggable brokers (AngelOne, Zerodha, etc.)

### 1.2 What is Algomin-UI?  
A Next.js-based frontend that:
- Renders candlestick charts and live tick data
- Consumes the `algomin` API endpoints
- Supports broker switching and customizable data feeds

---

## 2. Getting Started

### 2.1 Prerequisites
- Python 3.10+
- Node.js 16+
- Broker API credentials (AngelOne, Zerodha, etc.)

### 2.2 Installation
```bash```
# Clone repository
git clone https://github.com/your-org/algomin.git
cd algomin

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd algomin-ui
npm install

### 2.3 Configuration
Copy and populate the .env.example files in both algomin and algomin-ui:

ALGOMIN_API_BASE_URL=<your-backend-url>
ANGELONE_API_KEY=<…>
ANGELONE_CLIENT_ID=<…>
ANGELONE_PASSWORD=<…>
ANGELONE_TOTP_SECRET=<…>
ZERODHA_API_KEY=<…>
ZERODHA_SECRET=<…>
ZERODHA_TOKEN=<…>

## 3. Backend Architecture (`algomin`)

### 3.1 Project Layout

algomin/
├── src/
│ ├── config_loader/
│ ├── sessions/
│ ├── factory/
│ ├── clients/
│ ├── api/ # FastAPI routers
│ └── main.py
├── requirements.txt
└── .env.example



### 3.2 Core Concepts
- **BaseBrokerSession**: Abstract interface for all brokers  
- **BrokerFactory**: Registers and instantiates sessions  
- **Session Classes**: Implement `login()`, `get_auth_info()`, `fetch_candles()`, etc.  
- **FastAPI Routers**: Expose `/candles`, `/orders`, `/ws/stream`, etc.  

### 3.3 Adding a New Broker
1. Create a session class under `sessions/`, subclassing `BaseBrokerSession`.  
2. Implement required methods: `login()`, `get_auth_info()`, `fetch_candles()`.  
3. Register the session in  
   ```python
   BrokerFactory.register_broker("new_broker", NewBrokerSession)
4. Update frontend if special UI adjustments are needed.


## 4. API Reference
### 4.1 REST Endpoints
GET /api/candles

Query Params: broker, symbol, interval, from, to, limit, etc.

Returns: JSON array of candle objects

### 4.2 WebSocket Endpoints
WebSocket /ws/stream

Subscribes to live tick/candle updates

### 4.3 Error Handling
400 for validation errors

502 for upstream failures

Standardized error schema:

{ "detail": "Error message" }

## 5. Frontend Integration (algomin-ui)
### 5.1 Project Layout

algomin-ui/
├── pages/
│   ├── api/          # Next.js API proxy routes
│   ├── index.tsx     # Main chart page
│   └── _app.tsx
├── components/
├── styles/
└── .env.example

### 5.2 Fetching Data

pages/api/candles.ts: proxies to backend, preserves credentials
UI Hooks: useCandles(symbol, interval, from, to) for REST
WebSocket Hooks: useLiveData(broker) for streaming updates

### 5.3 Switching Brokers
Pass broker param in API calls

Update UI dropdown to select supported brokers

## 6. Contributing & Testing
Unit tests for sessions under /tests

Integration tests for API endpoints using pytest + httpx

UI tests with React Testing Library and Cypress

## 7. FAQs & Troubleshooting
CORS errors: ensure frontend origin is allowed in backend CORS settings
Authentication failures: verify TOTP and API keys in .env
High latency: enable caching in FastAPI (e.g., use Redis)