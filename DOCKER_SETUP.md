# One‑Shot Docker Setup (auto‑installs or shows commands)

If Docker isn’t installed, the script will **print exact install commands** for your OS.
On Ubuntu/Debian with sudo, it will **auto‑install** by default (override with `AUTO_INSTALL=0`).

## Download & run
```bash
chmod +x docker-one-shot-setup.sh
./docker-one-shot-setup.sh
```

### Optional flags
- `RESET=1` – prune containers/images/volumes first  
- `SKIP_HASH_REGEN=1` – skip `pip-compile` (dev quick mode)  
- `NO_CACHE=1` – force clean rebuild  
- `AUTO_INSTALL=0` – don’t auto-install Docker; just show commands

## What it does
1. If Docker is **missing**, prints the **install commands** for your OS (Ubuntu/Debian/Fedora/Arch/openSUSE/macOS).  
   On Ubuntu/Debian with sudo + `AUTO_INSTALL=1`, it runs those commands for you.
2. Ensures `/etc/docker/daemon.json` exists with BuildKit enabled (does not overwrite existing file).
3. Pulls base images with retries (`python:3.10-slim`, `node:20`).
4. Regenerates backend **pip hashes** inside the same base image (so hashes match what Docker downloads).
5. Writes a `PUBLIC_IP` into `.env` if missing.
6. Builds with **BuildKit**, starts services, tails logs, prints URLs.

## Tips
- Add mirrors/DNS in `/etc/docker/daemon.json` if pulls are slow:
  ```json
  { "features": { "buildkit": true },
    "registry-mirrors": ["https://mirror.gcr.io"],
    "dns": ["8.8.8.8","1.1.1.1"]
  }
  ```
- Low disk under Docker’s data-root? Move it and restart the daemon.
- Backend `--reload-*` warning? Add `watchfiles` to `apps/backend/requirements.txt` and rebuild.

Happy building 🚢
