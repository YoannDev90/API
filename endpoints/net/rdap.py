from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import httpx, ipaddress

@router.get("/rdap", tags=["tools"])
async def rdap_lookup(ip: str = Query(..., description="IP address")):
    try: ipaddress.ip_address(ip)
    except: raise HTTPException(status_code=400, detail="Invalid IP address")
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(f"https://rdap.db.ripe.net/ip/{ip}")
        d = resp.json()
        return {"code": "200", "ip": ip, "handle": d.get("handle"), "name": d.get("name"), "type": d.get("type"),
                "country": d.get("country"), "start_address": d.get("startAddress"), "end_address": d.get("endAddress"),
                "entities": [e.get("vcardArray",[[""]])[1][0][3] if e.get("vcardArray") else e.get("handle") for e in d.get("entities",[])[:5]]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

