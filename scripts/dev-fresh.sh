#!/usr/bin/env bash
set -euo pipefail

echo "▶️  Stopping and removing current stack (containers + named volumes)…"
docker compose down -v --remove-orphans || true

echo "🧹 Removing local caches…"
rm -rf \
  apps/ui/.next \
  apps/ui/.turbo \
  apps/ui/.vercel \
  apps/ui/.cache \
  **/__pycache__ \
  **/.pytest_cache || true

echo "🧽 Pruning Docker builder cache (keeps images/volumes)…"
docker buildx prune -f || docker builder prune -f || true

# Optional: check port clashes and warn (3003 UI, 5000 API by default)
echo "🔎 Checking ports 3003 and 5000…"
( command -v lsof >/dev/null 2>&1 && lsof -i :3003 -sTCP:LISTEN || true )
( command -v lsof >/dev/null 2>&1 && lsof -i :5000 -sTCP:LISTEN || true )

echo "🚀 Rebuilding and starting…"
docker compose --env-file .env up --build
