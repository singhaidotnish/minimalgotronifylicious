# One‑Shot Docker Setup for **minimalgotronifylicious**

This guide + script build and run the stack **reliably in one go**, including:
- pulling base images with retries,
- regenerating **secure pip hashes** for the backend on the correct platform,
- setting a sensible `PUBLIC_IP`,
- building with BuildKit and starting the services.

> TL;DR: run the script and you’re done.

---

## 0) Prereqs
- Docker Engine + Compose
- Run from the **repo root** (where `docker-compose.yml` lives).

## 1) Use the script
```bash
chmod +x docker-one-shot-setup.sh
./docker-one-shot-setup.sh
```

### Optional flags
```bash
RESET=1 ./docker-one-shot-setup.sh            # prune containers/images first
SKIP_HASH_REGEN=1 ./docker-one-shot-setup.sh  # skip pip-compile (dev only)
NO_CACHE=1 ./docker-one-shot-setup.sh         # full rebuild from scratch
```

## What the script does

1. **Checks Docker** is running and warns if low space under Docker’s data-root.
2. **Pulls base images** (`python:3.10-slim`, `node:20`) with automatic retries.
3. **Regenerates backend requirement hashes** inside `python:3.10-slim` so the
   hashes match exactly what your Docker build will download.
4. Ensures a `PUBLIC_IP` entry exists in your `.env` (best-effort guess).
5. Builds images with **BuildKit** and starts the stack.
6. Tails logs and prints the URLs:
   - UI: `http://localhost:3000`
   - API docs: `http://localhost:8000/docs`

## Notes

- If your backend shows `--reload-include/exclude have no effect`, add `watchfiles`
  to `apps/backend/requirements.txt` and rebuild:
  ```bash
  echo "watchfiles" >> apps/backend/requirements.txt
  DOCKER_BUILDKIT=1 docker compose build backend --no-cache
  ```

- If Docker Hub pulls are flaky, consider adding to `/etc/docker/daemon.json`:
  ```json
  {
    "features": { "buildkit": true },
    "registry-mirrors": ["https://mirror.gcr.io"],
    "dns": ["8.8.8.8", "1.1.1.1"]
  }
  ```
  then `sudo systemctl restart docker`.

- The script **does not modify** your Dockerfiles or compose. It only regenerates
  Python hashes and builds/starts. You’re safe to run it repeatedly.

---

Happy shipping 🚢
