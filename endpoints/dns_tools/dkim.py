from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver, hashlib

@router.get("/dkim", tags=["dns"])
async def dkim_check(domain: str = Query(..., description="Domain name"),
                     selector: str = Query(default="default", description="DKIM selector")):
    try:
        records = dns.resolver.resolve(f"{selector}._domainkey.{domain}", "TXT")
        record = str(records[0])
        parsed = {}
        for part in record.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                parsed[k.strip()] = v.strip()
        return {"code": "200", "domain": domain, "selector": selector, "has_dkim": True, "dkim": parsed}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return {"code": "200", "domain": domain, "selector": selector, "has_dkim": False, "dkim": None}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
