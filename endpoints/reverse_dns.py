from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket

@router.get("/reverse-dns", tags=["dns"])
async def reverse_dns(ip: str = Query(..., description="IP address")):
    try:
        hostname, aliases, ips = socket.gethostbyaddr(ip)
        return {"code": "200", "ip": ip, "hostname": hostname, "aliases": aliases}
    except socket.herror:
        return {"code": "200", "ip": ip, "hostname": None, "aliases": []}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
