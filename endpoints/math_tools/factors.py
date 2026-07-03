from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


@router.get("/factors", tags=["math"])
async def factorize(n: int = Query(..., description="Number to factor", ge=2)):
    remaining = n
    factors = []
    d = 2
    while d * d <= remaining:
        while remaining % d == 0:
            factors.append(d)
            remaining //= d
        d += 1 if d == 2 else 2
    if remaining > 1: factors.append(remaining)
    return {"code": "200", "n": n, "factors": factors}
