from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import datetime

@router.get("/cron", tags=["utils"])
async def cron_explain(expr: str = Query(..., description="Cron expression (e.g. '*/5 * * * *')")):
    try:
        from croniter import croniter
        now = datetime.datetime.now()
        cron = croniter(expr, now)
        next5 = [cron.get_next(datetime.datetime) for _ in range(5)]
        prev = croniter(expr, now).get_prev(datetime.datetime)
        return {"code": "200", "expression": expr, "previous_run": prev.isoformat(), "next_5_runs": [d.isoformat() for d in next5]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cron: {e}")

