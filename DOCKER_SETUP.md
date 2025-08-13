# One‑Shot Docker Setup (adds user to `docker` group)

Updates:
- If Docker isn’t installed, the script **prints OS-specific commands** and on Ubuntu/Debian can **auto‑install**.
- If Docker requires sudo, the script **adds your user to the `docker` group** (default). This lets you use Docker **without sudo** after you log out/in (or run `newgrp docker`).

## Run
```bash
chmod +x docker-one-shot-setup.sh
./docker-one-shot-setup.sh
```

### Flags
- `RESET=1` – prune containers/images/volumes first  
- `SKIP_HASH_REGEN=1` – skip `pip-compile` (dev speed)  
- `NO_CACHE=1` – force clean rebuild  
- `AUTO_INSTALL=0` – don’t auto-install Docker; just show commands  
- `ADD_TO_DOCKER_GROUP=0` – don’t modify user groups

After the first run (if you weren’t in the `docker` group), either:
```bash
newgrp docker   # apply group change to current shell
# or log out and back in
```

The rest of the flow is unchanged: it pulls base images (with retries), regenerates backend **pip hashes** on `python:3.10-slim`, builds with **BuildKit**, starts the stack, tails logs, and prints URLs.
