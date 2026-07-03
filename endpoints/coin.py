from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import secrets

@router.get("/coin", tags=["tools"])
async def coin_flip(count: int = Query(default=1, ge=1, le=100)):
    r = [secrets.choice(["heads","tails"]) for _ in range(count)]
    return {"code": "200", "count": count, "results": r, "heads": r.count("heads"), "tails": r.count("tails")}

