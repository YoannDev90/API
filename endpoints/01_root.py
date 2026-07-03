from fastapi import APIRouter, Request
from logging import getLogger

router = APIRouter()
logger = getLogger("api")


@router.get("/", tags=["general"])
async def read_root(request: Request):
    client_ip = request.scope.get("client_ip", request.client.host if request.client else "unknown")
    return {
        "code": "200",
        "message": "API Proxy",
        "version": "2.0.0",
        "client_ip": client_ip,
    }
