from __future__ import annotations
import os, importlib
from functools import lru_cache
from typing import Any, Dict, Optional, Callable
import yaml  # ensure PyYAML in requirements

REG_PATH = os.getenv(
    "BROKER_REGISTRY_PATH",
    "src/minimalgotronifylicious/config_loader/brokers.yaml"
)

def _truthy(v: str | bool | None, default=False) -> bool:
    if isinstance(v, bool): return v
    return (v or str(default)).strip().lower() in ("1","true","yes","on")

def paper_env_enabled() -> bool:
    # new name (preferred) + back-compat
    return _truthy(os.getenv("USE_PAPER"), False) or _truthy(os.getenv("PAPER_TRADING"), False)

@lru_cache(maxsize=1)
def load_registry() -> Dict[str, Any]:
    with open(REG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def import_ref(ref: str):
    """
    import_ref("pkg.mod:ClassOrFunc") -> object
    """
    module_path, name = ref.split(":")
    mod = importlib.import_module(module_path)
    return getattr(mod, name)

def make_client_from_registry(name: str, *, session: Any = None):
    reg = load_registry()
    item = reg.get(name)
    if not item:
        raise ValueError(f"Unsupported broker: {name}")

    cls = import_ref(item["import_path"])

    if name == "paper_trade":
        init_kwargs = {}
        ik = (item.get("init_kwargs") or {})
        seed_env = ik.get("seed_cash_env")
        default_seed = float(ik.get("default_seed", 100000))
        if seed_env:
            init_kwargs["seed_cash"] = float(os.getenv(seed_env, str(default_seed)))
        return cls(**init_kwargs)

    if item.get("needs_session"):
        return cls(session)
    return cls()

def get_symbols_provider(name: str) -> Callable[[], list[dict]]:
    reg = load_registry()
    item = reg.get(name)
    if not item:
        raise ValueError(f"Unsupported broker: {name}")
    ref = item.get("symbols_provider")
    if not ref:
        # safe fallback: empty list provider
        return lambda: []
    return import_ref(ref)

def defaults() -> dict:
    reg = load_registry()
    return reg.get("defaults", {})
