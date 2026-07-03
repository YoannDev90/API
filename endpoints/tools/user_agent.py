from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/user-agent", tags=["utils"])
async def user_agent_parse(ua: str = Query(..., description="User-Agent string")):
    try:
        from user_agents import parse
        p = parse(ua)
        return {"code": "200", "browser": {"family": p.browser.family, "version": p.browser.version_string},
                "os": {"family": p.os.family, "version": p.os.version_string},
                "device": {"family": p.device.family, "brand": p.device.brand or "", "model": p.device.model or ""},
                "is_mobile": p.is_mobile, "is_tablet": p.is_tablet, "is_pc": p.is_pc, "is_bot": p.is_bot}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"UA parse failed: {e}")

