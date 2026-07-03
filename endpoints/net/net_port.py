from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket, asyncio

@router.get("/net/port", tags=["network"])
async def net_port(host: str = Query(..., description="Hostname or IP"),
                   port: int = Query(..., description="Port number", ge=1, le=65535)):
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=3)
        writer.close()
        try: service = socket.getservbyport(port)
        except: service = "unknown"
        return {"code": "200", "host": host, "port": port, "open": True, "service": service}
    except: return {"code": "200", "host": host, "port": port, "open": False, "service": None}
