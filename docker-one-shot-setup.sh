#!/usr/bin/env bash
# docker-one-shot-setup.sh
# Build & run minimalgotronifylicious end-to-end.
# If Docker isn't installed, this script will:
#  - SHOW OS-specific install commands (always), and
#  - On Ubuntu/Debian WITH sudo, AUTO-INSTALL by default (override: AUTO_INSTALL=0)
#
# Usage:
#   chmod +x docker-one-shot-setup.sh
#   ./docker-one-shot-setup.sh
#
# Flags:
#   RESET=1            # prune containers/images first
#   SKIP_HASH_REGEN=1  # skip pip-compile (dev speed mode)
#   NO_CACHE=1         # full rebuild
#   AUTO_INSTALL=0     # show instructions only; don't auto-install Docker
#
set -euo pipefail

# ---------------- Config (override via env) ----------------
PY_IMAGE="${PY_IMAGE:-python:3.10-slim}"
NODE_IMAGE="${NODE_IMAGE:-node:20}"
BACKEND_DIR="${BACKEND_DIR:-apps/backend}"
FRONTEND_DIR="${FRONTEND_DIR:-apps/ui}"
MIN_GB="${MIN_GB:-4}"   # warn if Docker root has < MIN_GB free
PULL_RETRIES="${PULL_RETRIES:-3}"
RESET="${RESET:-0}"
SKIP_HASH_REGEN="${SKIP_HASH_REGEN:-0}"
AUTO_INSTALL="${AUTO_INSTALL:-1}"

# ---------------- Helpers ----------------
cecho(){ printf "\033[1;36m%s\033[0m\n" "$*"; }
gecho(){ printf "\033[1;32m%s\033[0m\n" "$*"; }
yecho(){ printf "\033[1;33m%s\033[0m\n" "$*"; }
recho(){ printf "\033[1;31m%s\033[0m\n" "$*"; }

need_cmd(){ command -v "$1" >/dev/null 2>&1 || { recho "Missing: $1"; exit 1; }; }

bytes_to_gb(){ awk -v b="$1" 'BEGIN{printf "%.1f", b/1024/1024/1024}'; }
get_free_bytes(){ df -PB1 --output=avail "$1" 2>/dev/null | tail -1 | tr -d ' '; }

can_sudo(){ sudo -n true 2>/dev/null || return 1; }

# Will set DOCKERCMD="docker" or "sudo docker"
choose_docker_cmd(){
  if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then DOCKERCMD="docker"; return 0; fi
    if can_sudo && sudo docker info >/dev/null 2>&1; then DOCKERCMD="sudo docker"; return 0; fi
  fi
  DOCKERCMD="docker" # default; may be installed shortly
}

retry_pull(){
  local img="$1" i
  for i in $(seq 1 "$PULL_RETRIES"); do
    if $DOCKERCMD pull "$img"; then return 0; fi
    yecho "pull $img attempt $i failed; retrying in $((i*5))s..."
    sleep $((i*5))
  done
  return 1
}

# ---------------- Detect OS ----------------
OS_ID=""; OS_CODENAME=""; OS_NAME="$(uname -s || true)"
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS_ID="${ID:-}"; OS_CODENAME="${VERSION_CODENAME:-}"
fi

print_install_instructions(){
  cecho "🐳 Docker is not installed. Run the following commands for your OS:"
  echo
  if [ "$OS_NAME" = "Darwin" ]; then
    cat <<'EOS'
# macOS (Homebrew)
brew install --cask docker
open -a Docker  # then wait for the whale icon to finish starting

# (optional) CLI plugins already included in Docker Desktop
EOS
  fi

  case "$OS_ID" in
    ubuntu|debian)
      cat <<'EOS'
# Ubuntu/Debian (official Docker repo)
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"  # log out & back in to use 'docker' without sudo
EOS
      ;;
    fedora)
      cat <<'EOS'
# Fedora
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
EOS
      ;;
    arch)
      cat <<'EOS'
# Arch Linux
sudo pacman -Syu --noconfirm docker docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
EOS
      ;;
    opensuse*)
      cat <<'EOS'
# openSUSE
sudo zypper install -y docker docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
EOS
      ;;
    *)
      cat <<'EOS'
# Generic Linux (visit docs if your distro differs)
# https://docs.docker.com/engine/install/
EOS
      ;;
  esac
  echo
}

# ---------------- Install Docker if missing (Ubuntu/Debian auto) ----------------
install_docker_if_missing(){
  if command -v docker >/dev/null 2>&1; then
    gecho "Docker already installed ✅"
    return 0
  fi

  print_install_instructions

  if [ "$AUTO_INSTALL" -eq 1 ] && [ "${OS_ID}" = "ubuntu" -o "${OS_ID}" = "debian" ]; then
    if ! can_sudo; then
      yecho "AUTO_INSTALL=1 but sudo not available. Please run the above commands manually."
      exit 1
    fi
    cecho "📦 AUTO-INSTALL: Ubuntu/Debian detected — running the commands shown above..."
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$OS_ID/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS_ID $OS_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo systemctl enable --now docker
    gecho "Docker installed ✅  (compose & buildx included)"
    yecho "Tip: add yourself to the docker group and re-login:  sudo usermod -aG docker \"$USER\""
  else
    yecho "AUTO-INSTALL disabled or unsupported distro. Please run the commands above, then re-run this script."
    exit 1
  fi
}

# ---------------- Ensure daemon.json sane (BuildKit on) ----------------
ensure_daemon_json(){
  local dj="/etc/docker/daemon.json"
  if [ -f "$dj" ]; then
    yecho "daemon.json exists; not modifying."
    return 0
  fi
  if can_sudo; then
    cecho "⚙️  Creating /etc/docker/daemon.json with BuildKit enabled"
    echo '{ "features": { "buildkit": true } }' | sudo tee "$dj" >/dev/null
    sudo systemctl restart docker || true
  else
    yecho "No sudo; skipping daemon.json setup (optional)."
  fi
}

# ---------------- Preflight checks ----------------
test -f docker-compose.yml || { recho "Run this from the repo root (docker-compose.yml not found)"; exit 1; }
test -d "$BACKEND_DIR" || { recho "Backend dir not found: $BACKEND_DIR"; exit 1; }
test -d "$FRONTEND_DIR" || { recho "Frontend dir not found: $FRONTEND_DIR"; exit 1; }
test -f "$BACKEND_DIR/requirements.txt" || { recho "Missing $BACKEND_DIR/requirements.txt"; exit 1; }

# Try to install Docker if needed
install_docker_if_missing

choose_docker_cmd

# Docker daemon reachability
if ! $DOCKERCMD info >/dev/null 2>&1; then
  if can_sudo; then
    yecho "Docker daemon not reachable; trying to start (systemd)..."
    sudo systemctl start docker || true
    sleep 1
  fi
  $DOCKERCMD info >/dev/null 2>&1 || { recho "Docker daemon still not running. Start Docker and re-run."; exit 1; }
fi

ensure_daemon_json

# Space check
DOCKER_ROOT="$($DOCKERCMD info --format '{{.DockerRootDir}}' 2>/dev/null || echo /var/lib/docker)"
FREE_B="$(get_free_bytes "$DOCKER_ROOT")"
FREE_GB="$(bytes_to_gb "${FREE_B:-0}")"
if [ -n "$FREE_B" ] && [ "$FREE_B" -lt $(( MIN_GB*1024*1024*1024 )) ]; then
  yecho "Low space under $DOCKER_ROOT: ${FREE_GB}GB free (< ${MIN_GB}GB). Consider moving data-root before big builds."
fi

# Optional reset
if [ "$RESET" -eq 1 ]; then
  cecho "🧹 Reset: docker compose down -v && docker system prune -af"
  $DOCKERCMD compose down -v || true
  $DOCKERCMD system prune -af || true
fi

# ---------------- Pull base images ----------------
cecho "📥 Pulling base images with retries..."
retry_pull "$PY_IMAGE" || { recho "Failed to pull $PY_IMAGE"; exit 1; }
retry_pull "$NODE_IMAGE" || { recho "Failed to pull $NODE_IMAGE"; exit 1; }

# ---------------- Regenerate Python hashes (optional) ----------------
if [ "$SKIP_HASH_REGEN" -eq 0 ]; then
  cecho "🔐 Regenerating backend requirements hashes inside $PY_IMAGE..."
  pushd "$BACKEND_DIR" >/dev/null
  awk '{gsub(/ --hash=sha256:[a-f0-9]+/,""); print}' requirements.txt > requirements.in
  $DOCKERCMD run --rm -v "$PWD":/app -w /app "$PY_IMAGE" /bin/bash -lc '
    pip install --no-cache-dir pip-tools && \
    pip-compile --generate-hashes --output-file=requirements.txt requirements.in
  '
  gecho "Hashes regenerated ✅"
  popd >/dev/null
else
  yecho "Skipping hash regeneration (SKIP_HASH_REGEN=1)"
fi

# ---------------- Ensure PUBLIC_IP in .env ----------------
if ! grep -q '^PUBLIC_IP=' .env 2>/div/null; then
  ip_guess="$(hostname -I 2>/dev/null | awk '{print $1}')"
  if [ -n "$ip_guess" ]; then
    cecho "🌐 Setting PUBLIC_IP=$ip_guess in .env (override later if needed)"
    echo "PUBLIC_IP=$ip_guess" >> .env
  fi
fi

# ---------------- Build & Run ----------------
cecho "🏗️  Building images (BuildKit)..."
export DOCKER_BUILDKIT=1
BUILD_FLAGS=(--progress=plain --pull)
[ "${NO_CACHE:-0}" -eq 1 ] && BUILD_FLAGS+=("--no-cache")
$DOCKERCMD compose "${BUILD_FLAGS[@]}" build

cecho "🚀 Starting services..."
$DOCKERCMD compose up -d

cecho "📜 Recent logs (Ctrl+C to stop)"
$DOCKERCMD compose logs -f --tail=80 || true

echo
gecho "✅ Done. Open:"
echo "  Frontend → http://localhost:3000"
echo "  Backend docs → http://localhost:8000/docs"
