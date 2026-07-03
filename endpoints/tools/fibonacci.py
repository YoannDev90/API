from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/fibonacci", tags=["tools"])
async def fibonacci(n: int = Query(default=10, ge=1, le=1000)):
    seq = [0, 1]
    for _ in range(2, n): seq.append(seq[-1] + seq[-2])
    return {"code": "200", "terms": n, "sequence": seq[:n]}

