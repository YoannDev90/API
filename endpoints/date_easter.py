from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime

@router.get("/date/easter", tags=["date"])
async def date_easter(year: int = Query(..., description="Year", ge=1, le=9999)):
    a = year % 19; b = year // 100; c = year % 100
    d = b // 4; e = b % 4; f = (b + 8) // 25
    g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    easter = datetime.date(year, month, day)
    ascension = easter + datetime.timedelta(days=39)
    pentecost = easter + datetime.timedelta(days=49)
    return {"code": "200", "year": year, "easter": str(easter), "ascension": str(ascension), "pentecost": str(pentecost)}
