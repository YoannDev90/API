from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import datetime

@router.get("/timestamp", tags=["utils"])
async def timestamp(value: int = Query(description="Unix timestamp in seconds")):
    try:
        dt = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        return {
            "code": "200", "unix_seconds": value,
            "iso_8601": dt.isoformat(),
            "utc": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "weekday": dt.strftime("%A"),
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timestamp")

