
# 🧠 minimalgotronifylicious

A minimal yet powerful monorepo for an AI-powered trading tool with clean separation of backend and frontend.

## 🗂 Folder Structure

```
minimalgotronifylicious/
├── apps/
│   ├── backend/    # FastAPI backend
│   └── ui/         # Next.js frontend (v15, Turbopack)
├── arch.drawio     # Architecture diagram (convert from .png/.dot if needed)
├── validate_structure.sh  # Monorepo validator script
└── README.md
```

## ⚙️ Tech Stack

| Layer       | Tech             |
|-------------|------------------|
| Frontend    | Next.js 15, React, TailwindCSS |
| Backend     | Python, FastAPI |
| Realtime    | WebSockets (`/ws/stream`) |
| REST APIs   | `/api/candles`, `/api/orders` |
| Assets/Data | `symbols.json`, `brokers.yaml` |
| Infra Ready | Railway, Render, Vercel        |

## 🚀 Quickstart

### 1. Backend (FastAPI)

```bash
cd apps/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit: [http://localhost:8000](http://localhost:8000)

### 2. Frontend (Next.js)

```bash
cd apps/ui
npm install
npm run dev
```

Visit: [http://localhost:3000](http://localhost:3000)

> 🔧 The frontend previously used `concurrently` to mock APIs. This has been removed since the monorepo now contains a real FastAPI backend.

### 3. Validate Structure

```bash
chmod +x validate_structure.sh
./validate_structure.sh
```

## 📊 Architecture

See [`minimalgotronifylicious_architecture.png`](./minimalgotronifylicious_architecture.png).

- Frontend talks to backend via REST + WebSocket
- Backend serves both static and dynamic data
- Future AI modules can be added under `apps/ai`

## 📌 Notes

- Keep `.env.example` files in both apps for easy onboarding.
- For future: Docker support, GitHub Actions CI/CD.

---

Built with ❤️ for focus-driven ADHD minds 🧠🚀
