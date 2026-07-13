from logging import getLogger
from fastapi import APIRouter, HTTPException, Query

logger = getLogger("api-proxy")
router = APIRouter()


@router.get("/temperature", tags=["tools"])
async def temperature(value: float = Query(..., description="Temperature value"),
                      unit: str = Query(default="celsius", description="Input unit: celsius, fahrenheit, kelvin")):
    u = unit.lower()
    if u in ("c", "celsius"):
        c, f, k = value, value * 9 / 5 + 32, value + 273.15
    elif u in ("f", "fahrenheit"):
        c, f, k = (value - 32) * 5 / 9, value, (value - 32) * 5 / 9 + 273.15
    elif u in ("k", "kelvin"):
        c, f, k = value - 273.15, (value - 273.15) * 9 / 5 + 32, value
    else:
        raise HTTPException(status_code=400, detail="Invalid unit. Use: celsius, fahrenheit, kelvin")
    return {"code": "200", "celsius": round(c, 2), "fahrenheit": round(f, 2), "kelvin": round(k, 2)}
