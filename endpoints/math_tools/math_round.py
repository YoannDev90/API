from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import math

@router.get("/math/round", tags=["math"])
async def math_round(value: float = Query(..., description="Value to round"),
                     decimals: int = Query(default=0, ge=0, le=10),
                     mode: str = Query(default="half_up", description="half_up|floor|ceil|trunc")):
    modes = {
        "half_up": lambda v, d: round(v, d),
        "floor": lambda v, d: math.floor(v * 10**d) / 10**d,
        "ceil": lambda v, d: math.ceil(v * 10**d) / 10**d,
        "trunc": lambda v, d: int(v * 10**d) / 10**d,
    }
    if mode not in modes: raise HTTPException(status_code=400, detail=f"Unknown mode: {mode}")
    return {"code": "200", "value": value, "rounded": modes[mode](value, decimals), "decimals": decimals, "mode": mode}
