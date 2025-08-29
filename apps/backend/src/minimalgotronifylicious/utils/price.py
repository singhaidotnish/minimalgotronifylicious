from typing import Any

def extract_price(val: Any) -> float:
    if isinstance(val, (int,float)): return float(val)
    if isinstance(val, str): return float(val.strip())

    if isinstance(val, dict):
        for k in ("ltp", "price", "last_price", "LastTradedPrice", "closePrice"):
            if k in val:
                try: return float(val[k])
                except: pass
        for v in val.values():
            try: return extract_price(v)
            except: continue

    if isinstance(val, (list, tuple)) and val:
        return extract_price(val[0])

    raise TypeError(f"Could not extract price from {type(val).__name__}: {val!r}")
