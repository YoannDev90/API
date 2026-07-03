from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import math

@router.get("/factorial", tags=["tools"])
async def factorial(n: int = Query(..., description="Number", ge=0, le=500)):
    return {"code": "200", "n": n, "factorial": math.factorial(n)}

