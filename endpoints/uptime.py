import time
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/uptime", tags=["general"])
async def uptime_check(request: Request):
    app = request.app
    if hasattr(app, "startup_time"):
        uptime = time.time() - app.startup_time
        return {
            "code": "200",
            "uptime_seconds": uptime,
            "uptime_human": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
        }
    return {"code": "200", "uptime": "unknown"}
