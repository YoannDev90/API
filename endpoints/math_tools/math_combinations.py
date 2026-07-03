from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import math

@router.get("/math/combinations", tags=["math"])
async def math_combinations(n: int = Query(..., description="Total items", ge=1),
                            k: int = Query(..., description="Items to choose", ge=1)):
    if k > n: raise HTTPException(status_code=400, detail="k must be <= n")
    return {"code": "200", "n": n, "k": k,
            "combinations": math.comb(n, k), "permutations": math.perm(n, k)}
