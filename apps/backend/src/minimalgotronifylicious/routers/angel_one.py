# apps/backend/routers/angel_one.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Literal

router = APIRouter(prefix="/api/angel-one", tags=["angel-one"])

class WireCondition(BaseModel):
    keyword: str
    params: Dict[str, str] = Field(default_factory=dict)
    label: str

class WireGroup(BaseModel):
    logic: Literal["AND", "OR"]
    blocks: List[WireCondition]

@router.post("/test")
def test_strategy(group: WireGroup):
    """
    Smoke-test endpoint. Later: map `group.blocks` to Angel One logic.
    For now we just echo back what we received and pretend success.
    """
    # Example validation: require at least one block
    if not group.blocks:
      raise HTTPException(status_code=400, detail="No blocks to test")

    # TODO: integrate SmartAPI here (login, token, LTP/quotes or a dry-run order)
    # For now, return simple, deterministic response:
    return {
        "ok": True,
        "received": group.model_dump(),
        "note": "Backend alive. Swap this stub with SmartAPI calls when ready."
    }
