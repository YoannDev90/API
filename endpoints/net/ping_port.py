from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket

@router.get("/ping", tags=["network"])
async def ping_host(host: str = Query(..., description="Hostname or IP"),
                    port: int = Query(default=80, ge=1, le=65535)):
    try:
        start = __import__("time").time()
        sock = socket.create_connection((host, port), timeout=5)
        elapsed = round((__import__("time").time() - start) * 1000, 1)
        sock.close()
        return {"code": "200", "host": host, "port": port, "reachable": True, "latency_ms": elapsed}
    except Exception:
        return {"code": "200", "host": host, "port": port, "reachable": False, "latency_ms": None}
