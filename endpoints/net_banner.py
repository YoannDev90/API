from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket, asyncio, time

@router.get("/net/banner", tags=["network"])
async def net_banner(host: str = Query(..., description="Hostname or IP"),
                     port: int = Query(default=80, ge=1, le=65535)):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=5)
        if port in (80, 8080):
            writer.write(f"HEAD / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
            await writer.drain()
            banner = (await asyncio.wait_for(reader.read(4096), timeout=3)).decode(errors="replace")
        else:
            banner = (await asyncio.wait_for(reader.read(4096), timeout=3)).decode(errors="replace")
        writer.close()
        return {"code": "200", "host": host, "port": port, "banner": banner[:2000]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
