from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import ipaddress

@router.get("/net/ip-range", tags=["network"])
async def net_ip_range(start: str = Query(..., description="Start IP"),
                       end: str = Query(..., description="End IP")):
    try:
        s = int(ipaddress.IPv4Address(start))
        e = int(ipaddress.IPv4Address(end))
        if e - s > 65536: return {"code": "200", "start": start, "end": end, "count": e - s + 1, "ips": [], "truncated": True}
        ips = [str(ipaddress.IPv4Address(i)) for i in range(s, e + 1)]
        return {"code": "200", "start": start, "end": end, "count": len(ips), "ips": ips}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
