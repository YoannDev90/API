from logging import getLogger
from fastapi import APIRouter, Query


logger = getLogger("api-proxy")
router = APIRouter()


import socket, asyncio

COMMON = [21,22,23,25,53,80,110,139,143,443,445,993,995,1433,1521,2049,3306,3389,5432,5900,6379,8080,8443,9000,27017]

@router.get("/net/common-ports", tags=["network"])
async def net_common_ports(host: str = Query(..., description="Hostname or IP")):
    results = []
    for port in COMMON:
        try:
            _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1)
            writer.close()
            try: service = socket.getservbyport(port)
            except: service = "unknown"
            results.append({"port": port, "service": service, "open": True})
        except: results.append({"port": port, "open": False})
    open_ports = [r for r in results if r["open"]]
    return {"code": "200", "host": host, "total_scanned": len(COMMON), "open_count": len(open_ports), "open_ports": open_ports}
