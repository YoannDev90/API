from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket, asyncio

DNSBL = ["zen.spamhaus.org", "b.barracudacentral.org", "bl.spamcop.net", "dnsbl.sorbs.net"]

@router.get("/sec/blacklist", tags=["security"])
async def sec_blacklist(ip: str = Query(..., description="IP address to check")):
    reversed_ip = ".".join(reversed(ip.split(".")))
    results = []
    for dnsbl in DNSBL:
        try:
            query = f"{reversed_ip}.{dnsbl}"
            await asyncio.get_event_loop().run_in_executor(None, lambda: socket.gethostbyname_ex(query))
            results.append({"dnsbl": dnsbl, "listed": True})
        except socket.gaierror: results.append({"dnsbl": dnsbl, "listed": False})
        except Exception as e: results.append({"dnsbl": dnsbl, "listed": False, "error": str(e)[:50]})
    listed_count = sum(1 for r in results if r["listed"])
    return {"code": "200", "ip": ip, "blacklisted": listed_count > 0, "listed_on": listed_count, "results": results}
