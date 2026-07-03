from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/mx-lookup", tags=["dns"])
async def mx_lookup(domain: str = Query(..., description="Domain name")):
    try:
        records = dns.resolver.resolve(domain, "MX")
        mx = []
        for r in records:
            mx.append({"priority": r.preference, "host": str(r.exchange).rstrip(".")})
        mx.sort(key=lambda x: x["priority"])
        return {"code": "200", "domain": domain, "mx_records": mx}
    except dns.resolver.NoAnswer:
        return {"code": "200", "domain": domain, "mx_records": []}
    except dns.resolver.NXDOMAIN:
        raise HTTPException(status_code=404, detail="Domain not found")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
