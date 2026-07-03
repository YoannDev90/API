from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dns/srv", tags=["dns"])
async def dns_srv(service: str = Query(..., description="SRV record (e.g. _sip._tcp.example.com)")):
    try:
        answers = dns.resolver.resolve(service, "SRV")
        records = [{"priority": r.priority, "weight": r.weight, "port": r.port, "target": str(r.target)} for r in answers]
        return {"code": "200", "service": service, "srv_records": records}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
