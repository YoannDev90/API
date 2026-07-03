from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import math

@router.get("/gcd", tags=["tools"])
async def gcd_lcm(a: int = Query(..., description="First number", ge=1),
                   b: int = Query(..., description="Second number", ge=1)):
    return {"code": "200", "a": a, "b": b, "gcd": math.gcd(a, b), "lcm": a * b // math.gcd(a, b)}

