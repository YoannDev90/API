from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/percentage", tags=["tools"])
async def percentage_calc(value: float = Query(..., description="Part value"),
                          total: float = Query(..., description="Total value", gt=0)):
    return {"code": "200", "value": value, "total": total, "percentage": round(value / total * 100, 2)}

