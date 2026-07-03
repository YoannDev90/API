from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx

RIR_URLS = {
    "RIPE": "https://rdap.db.ripe.net/ip/",
    "ARIN": "https://rdap.arin.net/registry/ip/",
    "APNIC": "https://rdap.apnic.net/ip/",
    "LACNIC": "https://rdap.lacnic.net/rdap/ip/",
    "AFRINIC": "https://rdap.afrinic.net/rdap/ip/",
}

@router.get("/net/rir", tags=["network"])
async def net_rir(ip: str = Query(..., description="IP address")):
    for name, base in RIR_URLS.items():
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                resp = await c.get(f"{base}{ip}")
            if resp.status_code == 200:
                return {"code": "200", "ip": ip, "rir": name, "handle": resp.json().get("handle")}
        except: pass
    return {"code": "200", "ip": ip, "rir": "unknown"}
