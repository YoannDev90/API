from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime

@router.get("/date/iso", tags=["date"])
async def date_iso(value: str = Query(..., description="ISO date string")):
    try:
        d = datetime.datetime.fromisoformat(value)
        if d.tzinfo is None: d = d.replace(tzinfo=datetime.timezone.utc)
        return {"code": "200", "original": value, "parsed": d.isoformat(),
                "year": d.year, "month": d.month, "day": d.day,
                "hour": d.hour, "minute": d.minute, "second": d.second,
                "tz": str(d.tzinfo), "unix": round(d.timestamp()),
                "weekday": d.strftime("%A"), "iso_week": d.isocalendar()[1]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
