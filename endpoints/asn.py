from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import httpx, ipaddress

@router.get("/asn", tags=["tools"])
async def asn_lookup(ip: str = Query(..., description="IP address")):
    try: ipaddress.ip_address(ip)
    except: raise HTTPException(status_code=400, detail="Invalid IP address")
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(f"https://rdap.db.ripe.net/ip/{ip}")
        if resp.status_code == 200:
            d = resp.json()
            asn_data = None
            for e in d.get("entities", []):
                for link in e.get("links", []):
                    if "autnum" in link.get("href", ""):
                        ar = await c.get(link["href"])
                        if ar.status_code == 200:
                            ad = ar.json()
                            asn_data = {"asn": ad.get("handle"), "name": ad.get("name"), "country": ad.get("country")}
                        break
                if asn_data: break
            return {"code": "200", "ip": ip, "asn": asn_data}
        return {"code": "200", "ip": ip, "asn": None}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

