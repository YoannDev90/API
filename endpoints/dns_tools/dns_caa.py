from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/dns/caa", tags=["dns"])
async def dns_caa(domain: str = Query(..., description="Domain name")):
    try:
        answers = dns.resolver.resolve(domain, "CAA")
        records = [{"flags": r.flags, "tag": r.tag.decode() if isinstance(r.tag, bytes) else r.tag, "value": r.value.decode() if isinstance(r.value, bytes) else r.value} for r in answers]
        return {"code": "200", "domain": domain, "caa_records": records}
    except dns.resolver.NoAnswer:
        return {"code": "200", "domain": domain, "caa_records": []}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
