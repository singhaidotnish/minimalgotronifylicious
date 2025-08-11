#!/usr/bin/env bash
# docker-one-shot-setup.sh
# Purpose: Build & run minimalgotronifylicious in one go with correct Python hashes,
#          resilient base-image pulls, and clean dev ergonomics.
#
# Usage:
#   chmod +x docker-one-shot-setup.sh
#   ./docker-one-shot-setup.sh                 # normal
#   SKIP_HASH_REGEN=1 ./docker-one-shot-setup.sh   # skip pip-compile (dev quick mode)
#   RESET=1 ./docker-one-shot-setup.sh             # prune old images/containers first
#   NO_CACHE=1 ./docker-one-shot-setup.sh          # force rebuild from scratch
#
set -euo pipefail

# ---------- Config (override via env) ----------
PY_IMAGE="${PY_IMAGE:-python:3.10-slim}"
NODE_IMAGE="${NODE_IMAGE:-node:20}"
BACKEND_DIR="${BACKEND_DIR:-apps/backend}"
FRONTEND_DIR="${FRONTEND_DIR:-apps/ui}"
MIN_GB="${MIN_GB:-4}"               # warn if Docker root has < MIN_GB free
SKIP_HASH_REGEN="${SKIP_HASH_REGEN:-0}"
RESET="${RESET:-0}"
NO_CACHE="${NO_CACHE:-0}"
PULL_RETRIES="${PULL_RETRIES:-3}"

# ---------- Helpers ----------
cecho(){ printf "\033[1;36m%s\033[0m\n" "$*"; }
gecho(){ printf "\033[1;32m%s\033[0m\n" "$*"; }
yecho(){ printf "\033[1;33m%s\033[0m\n" "$*"; }
recho(){ printf "\033[1;31m%s\033[0m\n" "$*"; }

need_cmd(){ command -v "$1" >/dev/null 2>&1 || { recho "Missing: $1"; exit 1; }; }

bytes_to_gb(){ awk -v b="$1" 'BEGIN{printf "%.1f", b/1024/1024/1024}'; }
get_free_bytes(){
  df -PB1 --output=avail "$1" 2>/dev/null | tail -1 | tr -d ' '
}

retry_pull(){
  local img="$1"
  local i
  for i in $(seq 1 "$PULL_RETRIES"); do
    if docker pull "$img"; then return 0; fi
    yecho "pull $img attempt $i failed; retrying in $((i*5))s..."
    sleep $((i*5))
  done
  return 1
}

# ---------- Preflight ----------
need_cmd docker
test -f docker-compose.yml || { recho "Run this from the repo root (docker-compose.yml not found)"; exit 1; }
test -d "$BACKEND_DIR" || { recho "Backend dir not found: $BACKEND_DIR"; exit 1; }
test -d "$FRONTEND_DIR" || { recho "Frontend dir not found: $FRONTEND_DIR"; exit 1; }
test -f "$BACKEND_DIR/requirements.txt" || { recho "Missing $BACKEND_DIR/requirements.txt"; exit 1; }

# Docker daemon
if ! docker info >/dev/null 2>&1; then
  yecho "Docker daemon not reachable; trying to start (systemd)..."
  sudo systemctl start docker || true
  sleep 1
  docker info >/dev/null 2>&1 || { recho "Docker daemon still not running. Start Docker and re-run."; exit 1; }
fi

# Space check
DOCKER_ROOT="$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || echo /var/lib/docker)"
FREE_B="$(get_free_bytes "$DOCKER_ROOT")"
FREE_GB="$(bytes_to_gb "${FREE_B:-0}")"
if [ -n "$FREE_B" ] && [ "$FREE_B" -lt $(( MIN_GB*1024*1024*1024 )) ]; then
  yecho "Low space under $DOCKER_ROOT: ${FREE_GB}GB free (< ${MIN_GB}GB). Consider moving data-root before big builds."
fi

# Optional reset
if [ "$RESET" -eq 1 ]; then
  cecho "🧹 Reset: docker compose down -v && docker system prune -af"
  docker compose down -v || true
  docker system prune -af || true
fi

# ---------- Step 1: Pull base images with retries ----------
cecho "📥 Pulling base images with retries..."
retry_pull "$PY_IMAGE" || { recho "Failed to pull $PY_IMAGE"; exit 1; }
retry_pull "$NODE_IMAGE" || { recho "Failed to pull $NODE_IMAGE"; exit 1; }

# ---------- Step 2: (Optional) Regenerate Python hashes on the same platform ----------
if [ "$SKIP_HASH_REGEN" -eq 0 ]; then
  cecho "🔐 Regenerating backend requirements hashes inside $PY_IMAGE..."
  pushd "$BACKEND_DIR" >/dev/null
  # Create requirements.in by stripping any '--hash=' fragments
  awk '{gsub(/ --hash=sha256:[a-f0-9]+/,""); print}' requirements.txt > requirements.in
  docker run --rm -v "$PWD":/app -w /app "$PY_IMAGE" /bin/bash -lc '
    pip install --no-cache-dir pip-tools && \
    pip-compile --generate-hashes --output-file=requirements.txt requirements.in
  '
  gecho "Hashes regenerated ✅"
  popd >/dev/null
else
  yecho "Skipping hash regeneration (SKIP_HASH_REGEN=1)"
fi

# ---------- Step 3: Ensure PUBLIC_IP in .env (optional) ----------
if ! grep -q '^PUBLIC_IP=' .env 2>/dev/null; then
  ip_guess="$(hostname -I 2>/dev/null | awk '{print $1}')"
  if [ -n "$ip_guess" ]; then
    cecho "🌐 Setting PUBLIC_IP=$ip_guess in .env (override later if needed)"
    echo "PUBLIC_IP=$ip_guess" >> .env
  fi
fi

# ---------- Step 4: Build with BuildKit ----------
cecho "🏗️  Building images (BuildKit)..."
export DOCKER_BUILDKIT=1
BUILD_FLAGS=(--progress=plain --pull)
[ "$NO_CACHE" -eq 1 ] && BUILD_FLAGS+=("--no-cache")
docker compose "${BUILD_FLAGS[@]}" build

# ---------- Step 5: Up & tail logs ----------
cecho "🚀 Starting services..."
docker compose up -d
cecho "📜 Recent logs (Ctrl+C to stop)"
docker compose logs -f --tail=80 || true

# ---------- Step 6: Print helpful URLs ----------
echo
gecho "✅ Done. Open:"
echo "  Frontend → http://localhost:3000"
echo "  Backend docs → http://localhost:8000/docs"
