from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import socket

@router.get("/ports", tags=["utils"])
async def port_scan(host: str = Query(..., description="Host to scan"),
                    ports: str = Query(default="22,80,443,8080", description="Comma-separated ports")):
    try:
        port_list = [int(p.strip()) for p in ports.split(",") if p.strip().isdigit()]
        open_ports = []
        for p in port_list:
            try:
                with socket.create_connection((host, p), timeout=1.5):
                    try: service = socket.getservbyport(p)
                    except: service = "unknown"
                    open_ports.append({"port": p, "service": service})
            except: pass
        return {"code": "200", "host": host, "open_ports": open_ports, "total_scanned": len(port_list), "total_open": len(open_ports)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Port scan failed: {e}")

