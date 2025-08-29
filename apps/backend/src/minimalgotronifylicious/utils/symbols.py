def normalize(raw: str, default_ex="NSE") -> tuple[str,str,str]:
    s = (raw or "").strip().upper()
    if ":" in s:
        ex, token = s.split(":", 1)
        ex = ex or default_ex
    else:
        ex, token = default_ex, s
    return ex, token, f"{ex}:{token}"
