from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


import httpx
from pydantic import BaseModel, Field

class WebhookInput(BaseModel):
    url: str = Field(..., description="Webhook URL")
    payload: dict = Field(default_factory=lambda: {"test": True, "timestamp": "2024-01-01T00:00:00Z"})

@router.post("/webhook/test", tags=["web"])
async def webhook_test(body: WebhookInput):
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            resp = await c.post(body.url, json=body.payload)
        return {"code": "200", "url": body.url, "status": resp.status_code,
                "response": resp.text[:2000], "success": resp.status_code < 500}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
