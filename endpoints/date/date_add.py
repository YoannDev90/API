from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime

@router.get("/date/add", tags=["date"])
async def date_add(date: str = Query(..., description="Start date (YYYY-MM-DD)"),
                   days: int = Query(default=0), months: int = Query(default=0), years: int = Query(default=0)):
    d = datetime.date.fromisoformat(date)
    import calendar
    y = d.year + years
    m = d.month + months
    while m > 12: y += 1; m -= 12
    while m < 1: y -= 1; m += 12
    max_day = calendar.monthrange(y, m)[1]
    d = d.replace(year=y, month=m, day=min(d.day, max_day))
    d += datetime.timedelta(days=days)
    return {"code": "200", "original": date, "result": str(d)}
