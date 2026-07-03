from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import dns.resolver

@router.get("/sec/email-auth", tags=["security"])
async def sec_email_auth(domain: str = Query(..., description="Domain name")):
    def get_txt(name):
        try: return [str(r) for r in dns.resolver.resolve(name, "TXT")]
        except: return []
    spf = [t for t in get_txt(domain) if t.startswith("v=spf1")]
    dmarc = [t for t in get_txt(f"_dmarc.{domain}") if t.startswith("v=DMARC1")]
    dkim_selectors = ["default", "google", "selector1", "mail", "dkim"]
    dkim = {}
    for sel in dkim_selectors:
        try:
            r = dns.resolver.resolve(f"{sel}._domainkey.{domain}", "TXT")
            dkim[sel] = str(r[0])[:200]
        except: pass
    return {"code": "200", "domain": domain, "spf": spf[0] if spf else None, "dmarc": dmarc[0] if dmarc else None, "dkim": dkim}
