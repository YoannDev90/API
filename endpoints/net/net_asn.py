from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

@router.get("/net/asn", tags=["network"])
async def net_asn(ip_or_asn: str = Query(..., description="IP address or AS number (e.g. 15169)")):
    import re
    try:
        if ip_or_asn.startswith("AS") or re.match(r"^\d+$", ip_or_asn):
            query = f"AS{ip_or_asn.lstrip('AS')}"
        else:
            query = ip_or_asn
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(f"https://rdap.db.ripe.net/autnum/{query.lstrip('AS')}" if query.startswith("AS") else f"https://rdap.db.ripe.net/ip/{query}")
        if resp.status_code == 200:
            d = resp.json()
            return {"code": "200", "query": ip_or_asn, "asn": d.get("handle"), "name": d.get("name"),
                    "country": d.get("country"), "type": d.get("type")}
        return {"code": "200", "query": ip_or_asn, "error": "Not found"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
