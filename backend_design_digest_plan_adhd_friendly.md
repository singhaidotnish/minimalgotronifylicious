# Backend Design Digest Plan (ADHD‑friendly)

> North Star: **One rule — dependency arrows only go right**. Keep HTTP (routers) → Services → Factory → Broker Client (Strategy) → External SDK. No back‑imports.

```
[ FastAPI Routers ]  ->  [ Services / Use‑Cases ]  ->  [ Factory -> Broker Strategy ]  ->  [ External SDK/API ]
          |                                             ^
          |---------------- Configuration / DI ---------|
```

---

## 1) Structure Map (what lives where & why)

### API / Routers (Controller pattern)
- **Only** HTTP/validation/DTO → calls services or direct client.
- **No** SDK imports; no business math.
- **Testing:** super fast route tests; import smokes.

**Unit test skeleton:**
```python
from fastapi.testclient import TestClient
from src.minimalgotronifylicious.api.main import app

def test_health():
    c = TestClient(app)
    r = c.get("/api/health")
    assert r.status_code == 200
```

### Services (Application/Use‑Case layer)
- Holds orchestration logic (P&L math, portfolio, order workflows).
- Makes code testable without HTTP.

### Brokers (Strategy + Adapter)
- One class per broker → implements `ltp`, `place_order`, etc.
- Wrap unstable I/O with **Retry + Timeout + Circuit Breaker**.
- **Lazy import** in the Factory to avoid circular imports.

### Factory (Factory pattern)
- Single place that selects the Strategy by **canonical id**: `angel_one`.
- **Reject** unrecognized ids.

```python
# src/.../brokers/order_client_factory.py
from dataclasses import dataclass

CANONICAL = "angel_one"

@dataclass
class OrderClientFactory:
    @staticmethod
    def create(broker: str, session):
        key = (broker or "").lower().replace("-", "_")
        if key != CANONICAL:
            raise ValueError(f"Unsupported broker: {broker} (use '{CANONICAL}')")
        from src.minimalgotronifylicious.brokers.angelone_smart_connect_client import AngelOneConnectClient
        return AngelOneConnectClient(session)
```

### Sessions
- Build/login to third‑party SDKs; inject into Strategy via Factory.

### Config Loader
- Read env/YAML, **normalize aliases at the edge** (map legacy → canonical) before factory.

---

## 2) Reliability Patterns (turn flaky into boring)

### Idempotent Consumer (prevent double orders)
- Require `X-Request-Id` on `/order`.
- Return the **same response** for the same id.

```python
import apps.backend.src.minimalgotronifylicious.routers.trading

_seen = {}


@router.post("/order")
def place_order(order: OrderIn, client=Depends(get_client),
                request_id: str | None = Header(default=None, convert_underscores=False)):
    if not request_id: raise HTTPException(400, "Missing X-Request-Id")
    key = f"order:{request_id}"
    if key in _seen: return _seen[key]
    res = apps.backend.src.minimalgotronifylicious.routers.trading.place_order(**order.model_dump())
    _seen[key] = res
    return res
```

**Upgrade path:** swap `_seen` with Redis:
```python
import redis
r = redis.Redis(host="redis", decode_responses=True)
if r.exists(key): return json.loads(r.get(key))
r.setex(key, 86400, json.dumps(res))
```

### Retry + Timeout + Jitter
```python
import time, random

def retry(fn, *, attempts=3, base=0.25, timeout=3.0):
    def run(*a, **k):
        for i in range(1, attempts+1):
            try:
                return fn(*a, **k)
            except Exception:
                if i==attempts: raise
                time.sleep(base*(2**(i-1)) + random.uniform(0, base/2))
    return run
```

### Circuit Breaker (fail fast, auto‑heal)
```python
import time
class CircuitBreaker:
    def __init__(self, fail_threshold=5, reset_after=30):
        self.n, self.until = 0, 0
    def call(self, fn, *a, **k):
        now = time.time()
        if now < self.until:
            raise RuntimeError("Broker temporarily unavailable")
        try:
            r = fn(*a, **k)
            self.n = 0
            return r
        except Exception:
            self.n += 1
            if self.n >= 5: self.until = now + 30
            raise
```

### Outbox + DLQ (never lose business events)
- Write event to `outbox` table same txn as state change.
- Worker publishes & marks sent; failures → `dead_letter` with reason.

---

## 3) Observability (see issues before users do)

### Structured Logging (JSON lines)
- Include: `request_id`, `user_id`, `order_id`, `endpoint`, `latency_ms`.

### Metrics (Prometheus)
- `http_requests_total{route,status}`
- `http_request_duration_seconds_bucket{route}` (p95)
- `broker_calls_total{op,status}`

### Tracing (OpenTelemetry)
- Span: route → service → broker call. Correlate failures quickly.

---

## 4) CI/CD Guardrails (fast, boring deploys)

**Pre‑merge:** import smokes, unit tests, ruff, mypy.
```bash
python -c "import src.minimalgotronifylicious.api as _; print('api ok')"
python -c "from src.minimalgotronifylicious.brokers.order_client_factory import OrderClientFactory; print('factory ok')"
python -m compileall apps/backend/src
```

**Deploy:** canary 10%, auto‑rollback on 5xx spike or SLO burn.

**Post‑deploy:** synthetic `/ltp` and `/order` dry‑run.

---

## 5) Paper Mode (demo today, money tomorrow)

**Strategy swap via Factory**
- `USE_PAPER=true` → `PaperClient` (in‑mem portfolio, orders)
- `USE_PAPER=false` → `AngelOneConnectClient`

```python
if os.getenv("USE_PAPER","true").lower()=="true":
    from .paper_client import PaperClient
    return PaperClient(seed_cash=float(os.getenv("DEMO_SEED_CASH","100000")))
```

**Endpoints to show value now**
- `GET /api/health`
- `GET /api/ltp?symbol=RELIANCE`
- `POST /api/order` (requires `X-Request-Id`)
- `GET /api/portfolio/snapshot`
- `GET /api/pnl/daily`
- `GET /api/orders`

---

## 6) Design Drills (build muscle memory)

1) **Add broker #2 (stub)**
- Create `zerodha_client.py` implementing same Strategy.
- Factory: `if key=="zerodha": return ZerodhaClient(...)`.

2) **Swap idempotency to Redis**
- Replace in‑mem `_seen` with Redis keys; TTL 24h.

3) **Add metrics**
- Wrap routes with a middleware that records latency + status.

4) **Add outbox**
- `orders_outbox(id, payload, status, error, ts)` + background publisher.

---

## 7) Three‑day Digest Schedule (20‑min blocks)

**Day 1** — Read map top‑to‑bottom; run import smokes; `make fresh`; hit 6 endpoints in paper mode.

**Day 2** — Add idempotency header to `/order`; add retry wrapper to broker calls.

**Day 3** — Add metrics; define SLOs: availability 99.5%, p95 `/order` < 800ms; add two alerts.

---

## 8) Quick Audit Checklist (copy/paste)
- [ ] Canonical broker id is `angel_one` everywhere (aliases only at env parsing if needed)
- [ ] Factory lazy‑imports adapters (no top‑level SDK imports)
- [ ] Routers don’t import SDKs or do business math
- [ ] Services hold orchestration (P&L/portfolio logic)
- [ ] Idempotent `/order` via `X-Request-Id`
- [ ] Retry + Timeout + Circuit Breaker around broker calls
- [ ] Structured logs + Prom metrics + trace spans
- [ ] Import smokes in CI; canary deploy; synthetic checks post‑deploy

---

## 9) Makefile “one‑buttons”
```makefile
demo: ## run backend in paper mode
	@export USE_PAPER=true DEMO_SEED_CASH=100000 && docker compose up --build

fresh: ## nuke caches and rebuild
	@docker compose down -v || true
	@docker builder prune -f || true
	@docker compose build --no-cache
	@USE_PAPER=true docker compose up --force-recreate
```

---

## 10) Glossary (quick meanings)
- **Strategy:** interchangeable client implementation per broker.
- **Factory:** returns the right Strategy based on canonical id.
- **Idempotent:** same request → same result (safe retries).
- **Outbox/DLQ:** reliable event delivery with a safety net.
- **SLO/Error Budget:** reliability promises & guardrails.

