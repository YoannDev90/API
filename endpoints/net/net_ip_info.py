from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import ipaddress

@router.get("/net/ip-info", tags=["network"])
async def net_ip_info(ip: str = Query(..., description="IP address")):
    try:
        a = ipaddress.ip_address(ip)
        return {"code": "200", "ip": ip, "version": a.version, "is_private": a.is_private, "is_loopback": a.is_loopback,
                "is_multicast": a.is_multicast, "is_link_local": a.is_link_local, "is_reserved": a.is_reserved,
                "is_global": a.is_global, "is_unspecified": a.is_unspecified, "reverse_name": a.reverse_pointer}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
