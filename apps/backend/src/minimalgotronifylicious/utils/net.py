import os, socket, logging
import requests
log = logging.getLogger(__name__)

def get_public_ip(cfg: dict | None = None) -> str:
    # 1) env/config wins
    ip = os.getenv("PUBLIC_IP") or (cfg or {}).get("public_ip")
    if ip:
        return ip

    # 2) try external
    try:
        return requests.get("https://api.ipify.org", timeout=2).text.strip()
    except Exception as e:
        log.info("Public IP lookup failed, using local IP: %s", e)

    # 3) fallback local
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "127.0.0.1"
