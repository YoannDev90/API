from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime, math

@router.get("/date/solstice", tags=["date"])
async def date_solstice(year: int = Query(..., description="Year", ge=1, le=9999)):
    # Approximate dates
    march_eq = datetime.date(year, 3, 20)
    june_sol = datetime.date(year, 6, 21)
    sept_eq = datetime.date(year, 9, 23)
    dec_sol = datetime.date(year, 12, 21)
    return {"code": "200", "year": year,
            "march_equinox": str(march_eq), "june_solstice": str(june_sol),
            "september_equinox": str(sept_eq), "december_solstice": str(dec_sol)}
