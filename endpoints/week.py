from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import datetime

@router.get("/week", tags=["tools"])
async def week_number(date: str = Query(default=None, description="Date (YYYY-MM-DD)")):
    d = datetime.date.fromisoformat(date) if date else datetime.date.today()
    iso = d.isocalendar()
    return {"code": "200", "date": str(d), "week": iso[1], "year": iso[0], "weekday": d.strftime("%A"), "day_of_year": d.timetuple().tm_yday}

