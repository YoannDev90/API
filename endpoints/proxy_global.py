import urllib.parse
from logging import getLogger

from fastapi import APIRouter, HTTPException, Request
from proxy import proxy_request
from config import config

router = APIRouter()
logger = getLogger("api-proxy")


@router.api_route(
    "/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    tags=["global-proxy"],
)
async def catch_all_proxy(request: Request, path: str):
    client_ip = request.scope.get("client_ip", "unknown")

    target_url = urllib.parse.unquote(path)
    if not target_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")

    blocked = ["localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]"]
    # check each blocked string individually instead of iterating through None
    if any(b in target_url for b in blocked):
        raise HTTPException(status_code=403, detail="Forbidden")
    if config.base_url and target_url.startswith(config.base_url):
        raise HTTPException(status_code=403, detail="Forbidden")

    logger.info(f"Global proxy: {request.method} -> {target_url} from {client_ip}")
    return await proxy_request(request, target_url=target_url)
