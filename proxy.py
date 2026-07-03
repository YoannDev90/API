import httpx
from starlette.responses import Response
from logging import getLogger
from config import config

logger = getLogger("api")


async def proxy_request(request, path: str):
    client_ip = request.scope.get(
        "client_ip", request.client.host if request.client else "unknown"
    )
    target_url = f"{config.data.base_url.rstrip('/')}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    logger.info(
        f"Proxy: {request.method} {request.url.path} -> {target_url} from {client_ip}"
    )

    try:
        body = await request.body()
        headers = {"user-agent": "API-Proxy/1.0", "accept": "*/*"}
        if body:
            headers["content-type"] = "application/octet-stream"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=False,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type"),
            )
    except httpx.TimeoutException:
        logger.error(f"Timeout proxying to {target_url}")
        return Response(
            '{"code": "504", "message": "Gateway Timeout"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        logger.error(f"Connection error proxying to {target_url}")
        return Response(
            '{"code": "502", "message": "Bad Gateway"}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"Proxy error for {target_url}: {e}")
        return Response(
            '{"code": "500", "message": "Internal Server Error"}',
            status_code=500,
            media_type="application/json",
        )


async def proxy_general(target_url: str, request):
    client_ip = request.scope.get(
        "client_ip", request.client.host if request.client else "unknown"
    )
    logger.info(f"General proxy: {request.method} -> {target_url} from {client_ip}")

    try:
        body = await request.body()
        headers = {"user-agent": "API-Proxy/1.0", "accept": "*/*"}
        if body:
            headers["content-type"] = "application/octet-stream"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=False,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type"),
            )
    except httpx.TimeoutException:
        return Response(
            '{"code": "504", "message": "Gateway Timeout"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError:
        return Response(
            '{"code": "502", "message": "Bad Gateway"}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        logger.error(f"General proxy error: {e}")
        return Response(
            '{"code": "500", "message": "Internal Server Error"}',
            status_code=500,
            media_type="application/json",
        )
