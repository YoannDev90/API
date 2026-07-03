from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import random

@router.get("/random/number", tags=["tools"])
async def random_number(min: int = Query(default=0), max: int = Query(default=100), count: int = Query(default=1, ge=1, le=100)):
    return {"code": "200", "min": min, "max": max, "count": count, "numbers": [random.randint(min, max) for _ in range(count)]}

