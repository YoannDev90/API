from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/leap", tags=["tools"])
async def leap_year(year: int = Query(..., description="Year", ge=1, le=9999)):
    leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    return {"code": "200", "year": year, "leap": leap, "days": 366 if leap else 365}

