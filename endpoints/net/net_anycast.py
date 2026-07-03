from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket

@router.get("/net/anycast", tags=["network"])
async def net_anycast(ip: str = Query(..., description="IP address")):
    try:
        import ipaddress
        a = ipaddress.ip_address(ip)
        likely_anycast = any([
            str(a).startswith("1.1.1.") or str(a).startswith("1.0.0."),
            str(a).startswith("8.8.8.") or str(a).startswith("8.8.4."),
            str(a).startswith("9.9.9."),
            str(a).startswith("208.67.222.") or str(a).startswith("208.67.220."),
            str(a).startswith("185.228.168.") or str(a).startswith("185.228.169."),
            str(a).startswith("76.76."),
        ])
        return {"code": "200", "ip": ip, "likely_anycast": likely_anycast,
                "note": "Anycast detection is heuristic. Known DNS/CDN anycast IPs are flagged."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
