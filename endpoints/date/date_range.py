from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime

@router.get("/date/range", tags=["date"])
async def date_range(start: str = Query(..., description="Start (YYYY-MM-DD)"),
                     end: str = Query(..., description="End (YYYY-MM-DD)"),
                     step: int = Query(default=1, ge=1)):
    s = datetime.date.fromisoformat(start)
    e = datetime.date.fromisoformat(end)
    dates = []
    current = s
    while current <= e:
        dates.append(str(current))
        current += datetime.timedelta(days=step)
    return {"code": "200", "start": start, "end": end, "count": len(dates), "dates": dates[:365]}
