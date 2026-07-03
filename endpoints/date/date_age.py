from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import datetime

@router.get("/date/age", tags=["tools"])
async def age_calculator(birth: str = Query(..., description="Birth date (YYYY-MM-DD)")):
    b = datetime.date.fromisoformat(birth)
    today = datetime.date.today()
    age = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
    nb = datetime.date(today.year + (0 if (today.month, today.day) <= (b.month, b.day) else 1), b.month, b.day)
    return {"code": "200", "birth": birth, "age": age, "next_birthday": str(nb), "days_to_next": (nb - today).days}

