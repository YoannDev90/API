from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime

@router.get("/date/weekday", tags=["date"])
async def date_weekday(date: str = Query(..., description="Date (YYYY-MM-DD)")):
    d = datetime.date.fromisoformat(date)
    iso = d.isocalendar()
    return {"code": "200", "date": date, "day_name": d.strftime("%A"), "day_short": d.strftime("%a"),
            "weekday": d.weekday(), "iso_weekday": iso[2], "week_number": iso[1], "year": iso[0],
            "day_of_year": d.timetuple().tm_yday}
