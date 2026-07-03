from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket, time

@router.get("/net/latency", tags=["network"])
async def net_latency(host: str = Query(..., description="Hostname or IP"),
                      count: int = Query(default=3, ge=1, le=10)):
    times = []
    for _ in range(count):
        try:
            start = time.time()
            sock = socket.create_connection((host, 80), timeout=3)
            elapsed = (time.time() - start) * 1000
            sock.close()
            times.append(round(elapsed, 1))
        except: pass
    if not times: raise HTTPException(status_code=502, detail="Host unreachable")
    return {"code": "200", "host": host, "latency_ms": times, "avg": round(sum(times)/len(times), 1), "min": min(times), "max": max(times)}
