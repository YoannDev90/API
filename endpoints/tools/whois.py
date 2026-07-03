from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/whois", tags=["utils"])
async def whois_lookup(domain: str = Query(..., description="Domain name to query")):
    import whois
    try:
        w = whois.whois(domain)
        data = {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": _fmt(w.creation_date),
            "expiration_date": _fmt(w.expiration_date),
            "updated_date": _fmt(w.updated_date),
            "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else None,
            "status": w.status, "emails": w.emails, "org": w.org, "country": w.country,
            "dnssec": w.dnssec, "whois_server": w.whois_server,
            "raw": w.text[:4096] if w.text else None,
        }
        data = {k: v for k, v in data.items() if v not in (None, "", [], {}, "N/A")}
        return {"code": "200", "data": data}
    except Exception as e:
        logger.error(f"WHOIS lookup failed for {domain}: {e}")
        raise HTTPException(status_code=502, detail=f"WHOIS lookup failed: {e}")

def _fmt(d):
    if not d: return None
    if isinstance(d, list): return [str(x) for x in d if x]
    return str(d)

