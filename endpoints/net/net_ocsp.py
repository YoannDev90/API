from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/ocsp", tags=["network"])
async def net_ocsp(domain: str = Query(..., description="Domain name"),
                   port: int = Query(default=443, ge=1, le=65535)):
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(f"https://{domain}:{port}")
        ocsp = resp.headers.get("ocsp-response") or resp.headers.get("x-ocsp-response")
        return {"code": "200", "domain": domain, "must_staple": False,
                "ocsp_header": bool(ocsp), "ocsp_response": bool(ocsp)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
