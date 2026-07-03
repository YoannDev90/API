from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


@router.get("/is-prime", tags=["math"])
async def is_prime(n: int = Query(..., description="Number to test", ge=2)):
    if n < 2: return {"code": "200", "n": n, "prime": False}
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0: return {"code": "200", "n": n, "prime": False}
    return {"code": "200", "n": n, "prime": True}
