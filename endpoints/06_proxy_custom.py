import ipaddress
import socket
from logging import getLogger
from typing import Optional, Dict, Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

router = APIRouter()
logger = getLogger("api")


class ProxyRequest(BaseModel):
    url: str = Field(..., description="Destination URL")
    method: str = Field(default="GET", description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(default=None)
    data: Optional[str] = Field(default=None)
    json_data: Optional[Dict[str, Any]] = Field(default=None)
    timeout: Optional[int] = Field(default=30, ge=1, le=300)


@router.post("/proxy", tags=["proxy"])
async def custom_proxy(proxy_req: ProxyRequest, request: Request):
    client_ip = request.scope.get("client_ip", request.client.host if request.client else "unknown")

    if not proxy_req.url.startswith(("http://", "https://")):
        return Response("URL must start with http:// or https://", status_code=400)

    # SSRF protection
    try:
        hostname = proxy_req.url.split("://")[1].split("/")[0].split(":")[0]
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback:
                return Response("Access to private/local IPs not allowed", status_code=403)
        except ValueError:
            try:
                resolved = socket.gethostbyname(hostname)
                ip = ipaddress.ip_address(resolved)
                if ip.is_private or ip.is_loopback:
                    raise HTTPException(status_code=403, detail="Access to private/local IPs not allowed")
            except socket.gaierror:
                pass
    except Exception:
        pass

    try:
        data = proxy_req.json_data or proxy_req.data
        async with httpx.AsyncClient(timeout=proxy_req.timeout) as client:
            resp = await client.request(
                method=proxy_req.method.upper(),
                url=proxy_req.url,
                headers=proxy_req.headers,
                json=data if isinstance(data, dict) else None,
                content=data if isinstance(data, str) else None,
                follow_redirects=False,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type"),
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway Timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail="Bad Gateway")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
