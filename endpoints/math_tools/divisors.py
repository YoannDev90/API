from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


@router.get("/divisors", tags=["math"])
async def divisors(n: int = Query(..., description="Number", ge=1)):
    divs = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i: divs.append(n // i)
    return {"code": "200", "n": n, "divisors": sorted(divs), "count": len(divs)}
