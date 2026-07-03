from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import datetime

@router.get("/date/diff", tags=["tools"])
async def date_diff(start: str = Query(..., description="Start date (YYYY-MM-DD)"),
                    end: str = Query(..., description="End date (YYYY-MM-DD)")):
    s = datetime.date.fromisoformat(start)
    e = datetime.date.fromisoformat(end)
    days = (e - s).days
    return {"code": "200", "start": start, "end": end, "days": abs(days), "weeks": round(abs(days)/7,1),
            "months": round(abs(days)/30.44,1), "years": round(abs(days)/365.25,1),
            "direction": "forward" if days >= 0 else "backward"}

