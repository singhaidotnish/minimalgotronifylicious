start_websocket.py
├── session = AngelOneSession(...)       ✅ Login & credentials
├── ws_client = AngelOneWebSocketV2Client(session)   ✅ WebSocket client
├── ws_client.set_callbacks(...)         ✅ Hand over control
├── ws_client.connect()                  ✅ Establish connection
├── ws_client.subscribe(...)             ✅ Send tokens
└── ws_client.run_forever()              ✅ Wait for ticks (calls .on_data)


# 🚀 First Steps with Algomin

Welcome to **Algomin**, your configurable algorithmic trading assistant.

This guide will walk you through the basic setup and first usage of the tool — whether you're a developer or a trader trying out pre-built strategies.

---

## ✅ Prerequisites

- Python 3.10+ installed  
- `pip` or `poetry` for managing dependencies  
- A broker account (e.g., Zerodha) with API credentials  
- (Optional) Docker installed if running via container

---

## 📦 1. Install Dependencies

Clone the repository:

```bash
git clone https://github.com/yourusername/algomin.git
cd minimalgotronifylicious
```
#### Install requirements:

pip install -r requirements.txt


#### Configure API Credentials
Create a .env file (or edit config.yaml if you're using YAML-based secrets):

ini
Copy
Edit
API_KEY=your_api_key
API_SECRET=your_api_secret
REDIRECT_URI=https://yourapp.com/callback

#### Understand the Folder Structure #TODO add latest folders

algomin/ – Core logic (strategy classes, factory, broker clients)
data/ – YAML configs for stocks, derivatives, and common settings
live/ – Live trading modules (e.g., bracket_order_derivative_stock.py)
web/ – (Optional) UI components using FastAPI/React
tests/ – Unit and integration tests
scripts/ – Helper scripts (e.g., authentication, data sync)

#### Try a Sample Bracket Order
Run this command to place a test bracket order:

python -m live.bracket_order_derivative_stock --config data/sample_order.yaml

> Example sample_order.yaml:

> symbol: NIFTY
exchange: NFO
order_type: bracket
transaction_type: BUY
quantity: 50
strategy: simple_momentum


#### Try a simple limit order
Run this command to place a etst limit order:

python -m algomin.start_websocket 

#### Run Web Interface (Optional)
Start the FastAPI server:

uvicorn main:app --reload

Visit in your browser:

http://localhost:8000


#### Run Tests
Use pytest to validate functionality:

pytest


#### Learn and Customize Strategies
Explore and modify strategies:

See strategies/ for available strategies
Use data/bo_derivative_data.yaml to define order parameters
Use inline comments in YAML files for clarity
Documentation coming soon!


#### Need Help?
Open an issue on GitHub
Or email: support@algomin.io