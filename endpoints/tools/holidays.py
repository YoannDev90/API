from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import datetime

@router.get("/holidays", tags=["date"])
async def holidays(year: int = Query(default=None, description="Year"),
                   country: str = Query(default="US", description="ISO country code (US, FR, GB, DE, JP...)")):
    year = year or datetime.date.today().year
    try:
        import holidays
        h = holidays.country_holidays(country, years=year)
        results = [{"date": str(d), "name": n} for d, n in sorted(h.items())]
        return {"code": "200", "year": year, "country": country, "count": len(results), "holidays": results}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
