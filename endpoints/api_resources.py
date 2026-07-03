import asyncio
from logging import getLogger

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from config import config

router = APIRouter()
logger = getLogger("api")


@router.api_route("/api/resources", methods=["GET"], tags=["internal-proxy"])
async def resources_proxy(request: Request):
    target_url = f"{config.data.base_url.rstrip('/')}/resources"
    if request.url.query:
        target_url += f"?{request.url.query}"

    body = await request.body()
    headers = {"user-agent": "API-Proxy/1.0", "accept": "*/*"}
    if body:
        headers["content-type"] = "application/octet-stream"

    client = httpx.AsyncClient(timeout=30.0)
    stream_cm = None
    response = None

    try:
        stream_cm = client.stream(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            follow_redirects=False,
        )
        response = await stream_cm.__aenter__()

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Origin error: {response.status_code}",
            )

        async def generate():
            try:
                async for chunk in response.aiter_text():
                    yield chunk
                    await asyncio.sleep(0.01)
            except Exception as e:
                logger.error(f"SSE stream error: {e}")
            finally:
                if stream_cm and response:
                    try:
                        await stream_cm.__aexit__(None, None, None)
                    except Exception:
                        pass

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SSE proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
