from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver, ipaddress

@router.get("/dns/ptr", tags=["dns"])
async def dns_ptr(ip: str = Query(..., description="IP address")):
    try:
        addr = ipaddress.ip_address(ip)
        if isinstance(addr, ipaddress.IPv4Address): ptr_name = ".".join(reversed(ip.split("."))) + ".in-addr.arpa"
        else: ptr_name = ".".join(reversed(list(addr.exploded.replace(":","")))) + ".ip6.arpa"
        answers = dns.resolver.resolve(ptr_name, "PTR")
        return {"code": "200", "ip": ip, "ptr_records": [str(r) for r in answers]}
    except dns.resolver.NXDOMAIN:
        return {"code": "200", "ip": ip, "ptr_records": []}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
