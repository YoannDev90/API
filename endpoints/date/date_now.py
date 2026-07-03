from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime

@router.get("/date/now", tags=["date"])
async def date_now(tz: str = Query(default=None, description="Timezone (e.g. Europe/Paris)")):
    try:
        if tz:
            from zoneinfo import ZoneInfo
            t = datetime.datetime.now(ZoneInfo(tz))
        else:
            t = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        return {"code": "200", "timezone": tz or "UTC", "iso": t.isoformat(),
                "date": t.strftime("%Y-%m-%d"), "time": t.strftime("%H:%M:%S"),
                "unix": round(t.timestamp()), "weekday": t.strftime("%A")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
