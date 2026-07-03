from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dns/soa", tags=["dns"])
async def dns_soa(domain: str = Query(..., description="Domain name")):
    try:
        soa = dns.resolver.resolve(domain, "SOA")[0]
        return {"code": "200", "domain": domain, "soa": {"mname": str(soa.mname), "rname": str(soa.rname),
                "serial": soa.serial, "refresh": soa.refresh, "retry": soa.retry, "expire": soa.expire, "minimum": soa.minimum}}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
