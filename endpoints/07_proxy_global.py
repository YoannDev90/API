import base64
import urllib.parse
from logging import getLogger

from fastapi import APIRouter, HTTPException, Request
from proxy import proxy_general
from config import config

router = APIRouter()
logger = getLogger("api")


@router.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"], tags=["global-proxy"])
async def catch_all_proxy(request: Request, path: str):
    client_ip = request.scope.get("client_ip", request.client.host if request.client else "unknown")

    # Decode target URL: base64 url-safe, base64 standard, url-encoded, or raw
    target_url = None
    for decoder in [
        lambda p: base64.urlsafe_b64decode(p).decode(),
        lambda p: base64.b64decode(p).decode(),
        lambda p: urllib.parse.unquote(p),
    ]:
        try:
            target_url = decoder(path)
            break
        except Exception:
            continue

    if not target_url and path.startswith(("http://", "https://")):
        target_url = path

    if not target_url:
        raise HTTPException(status_code=400, detail="Invalid encoded URL")

    # Block internal URLs
    blocked = ["localhost", "127.0.0.1", "0.0.0.0"]
    if any(b in target_url for b in blocked):
        raise HTTPException(status_code=403, detail="Forbidden")
    if config.data.base_url and target_url.startswith(config.data.base_url):
        raise HTTPException(status_code=403, detail="Forbidden")

    logger.info(f"Global proxy: {request.method} -> {target_url} from {client_ip}")
    return await proxy_general(target_url, request)
