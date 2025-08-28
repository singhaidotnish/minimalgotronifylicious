
# Minimalgotronifylicious — Backend Design Map (ADHD-Friendly)

> TL;DR: 4 boxes + one rule. Keep HTTP (routers) separate from Brokers (SDK adapters). Use a tiny Factory.
> When anything breaks, smoke‑test imports first, not the whole server.

---

## 0) One‑Screen Mental Model (Clean-ish)
```
[ FastAPI Routers ]  ->  [ Use-Cases / Services (optional) ]  ->  [ Factory -> Broker Client ]  ->  [ External SDK/API ]
          |                                           ^
          |-------------- Configuration / DI ---------|
```

**Dependency rule:** arrows only go **rightwards** (or inward). Routers never get imported by Brokers.

---

## 1) Canonical Broker Name (reduce ADHD noise)
- Choose **ONE** internal id: `angel_one` (canonical).
- Allow legacy names (`angel_one`, `angelone`) **only at the boundary** (env parsing), NOT in code.
- Result: Factory only switches on `angel_one` (clear), while a normalization step maps any alias to `angel_one` before it reaches the factory.

✅ Short-term: keep an alias map to avoid breakage.  
✅ Long-term: remove the alias map and enforce `BROKER=angel_one` everywhere.

---

## 2) Files by responsibility
- `api/routers/*.py` → HTTP endpoints only (FastAPI). Zero SDK imports.
- `brokers/angelone_angel_one_client.py` → AngelOne adapter (Strategy) implementing `place_order/ltp/...`.
- `brokers/order_client_factory.py` → Factory (creates the right adapter). **Lazy-import** adapters to avoid circulars.
- `sessions/angelone_session.py` → builds/logs in to session (separate from adapter).
- `config_loader/*` → environment + YAML readers. May normalize names (`angel_one`→`angel_one`).

Each folder has an `__init__.py`. Docker sets `PYTHONPATH=/app`.

---

## 3) Request flow (example: /api/order)
1. Router parses request → `Depends(get_order_client)`.
2. `get_order_client()` builds a session and calls `OrderClientFactory.create("angel_one", session)`.
3. Factory lazy-imports `AngelOneConnectClient` and returns it.
4. Adapter calls real SDK (or stub if `PAPER_TRADING=true`).

---

## 4) Factory (canonical + lazy import)
```python
from __future__ import annotations
from dataclasses import dataclass

# Keep aliases ONLY in env parsing (not required inside the factory)
CANONICAL = "angel_one"

@dataclass
class OrderClientFactory:
    @staticmethod
    def create(broker_name: str, session):
        key = (broker_name or "").lower().replace("-", "_")
        if key != CANONICAL:
            raise ValueError(f"Unsupported broker: {broker_name} (use 'angel_one')")

        # Lazy import prevents boot-time explosions & circular imports
        from src.minimalgotronifylicious.brokers.angelone_angel_one_client import AngelOneConnectClient
        return AngelOneConnectClient(session)
```
> If you still have old values like `angel_one`, normalize them BEFORE calling `create()`.

---

## 5) Router DI pattern (simple and stable)
```python
from fastapi import APIRouter, Depends
from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory
from src.minimalgotronifylicious.sessions.angelone_session import AngelOneSession

router = APIRouter(prefix="/api")

def get_order_client():
    sess = AngelOneSession.from_env()
    return OrderClientFactory.create("angel_one", sess)

@router.get("/ltp")
def ltp(symbol: str, client = Depends(get_order_client)):
    return client.ltp(symbol)

@router.post("/order")
def place_order(order: dict, client = Depends(get_order_client)):
    return client.place_order(order)
```

---

## 6) CI/CD — Import smoke tests (fast feedback)
Run these in CI before starting Uvicorn:
```bash
python -c "import src.minimalgotronifylicious.api as _; print('api ok')"
python -c "from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory; print('factory ok')"
```

Optional pytest stub:
```python
def test_imports():
    import src.minimalgotronifylicious.api as _
    from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory
```

---

## 7) Make targets (ADHD one‑buttons)
- `make fresh` → down + prune caches + full rebuild + up
- `make dev` → rebuild + up
- `make logs` → tail all

If failure repeats, try: `docker compose build --no-cache && docker compose up --force-recreate`

---

## 8) Troubleshooting ImportError (checklist)
- Does `order_client_factory.py` have **no top-level adapter import**? (must be lazy inside `create()`)
- Are all `__init__.py` present?
- Is `PYTHONPATH=/app` set in Docker?
- Is the adapter import path correct?
  `src.minimalgotronifylicious.brokers.angelone_angel_one_client` (not a relative from router)
- Can you import in isolation?
  ```bash
  python -c "from src.minimalgotronifylicious.brokers.angelone_angel_one_client import AngelOneConnectClient; print('ok')"
  ```

---

## 9) Migration plan to canonical name
1. Set `BROKER=angel_one` in `.env*`, Docker, CI secrets.c
2. In any code that used `"angel_one"`, switch to `"angel_one"`.
3. Keep a temporary alias map at env parsing (optional) with a deprecation log.
4. After a week of green builds, delete the alias map.

---

## 10) ADHD quick ritual to “appreciate the design”
- Open this doc.
- Run the two **import** smoke tests.
- Open `order_client_factory.py` and confirm: **no top‑level adapter imports**.
- Search for `"angel_one"` in the repo — replace with `"angel_one"` except in env normalization.
- Run `make fresh` and hit `/api/health` then `/api/ltp?symbol=TCS`.

You’re done. Next skill-up: add a second broker file and a second `if key == "zerodha": …` in the factory to feel the win.

---

## 11) Reference checklist (copy/paste)
- [ ] Canonical broker id is `angel_one`.
- [ ] Factory lazy‑imports adapter.
- [ ] Routers don’t import SDKs.
- [ ] Sessions live in `sessions/`.
- [ ] `PYTHONPATH=/app` in Docker.
- [ ] Import smoke tests in CI.
- [ ] `make fresh` succeeds locally.
