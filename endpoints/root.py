from fastapi import APIRouter, Request
from __init__ import __version__

router = APIRouter()


@router.get("/", tags=["general"])
async def read_root(request: Request):
    client_ip = request.scope.get("client_ip", "unknown")
    return {
        "code": "200",
        "message": "API Proxy",
        "version": __version__,
        "client_ip": client_ip,
    }
