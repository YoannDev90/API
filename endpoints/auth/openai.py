import asyncio
import json
import os
from logging import getLogger
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

logger = getLogger("api-proxy")
router = APIRouter(prefix="/auth/v1", include_in_schema=False)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")


async def require_auth(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
    key = auth.split(" ", 1)[1]
    if not key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if OPENAI_API_KEY and key != OPENAI_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


async def _proxy(method: str, path: str, body: dict | None, request: Request):
    url = f"{OPENAI_BASE_URL}/{path}"
    headers = {
        "Authorization": request.headers.get("Authorization", ""),
        "Content-Type": "application/json",
    }
    is_stream = body and body.get("stream", False) if body else False

    try:
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as c:
            if is_stream:
                req = c.build_request(method, url, json=body, headers=headers)
                resp = await c.send(req, stream=True)
                resp.raise_for_status()

                async def stream():
                    try:
                        async for chunk in resp.aiter_lines():
                            if chunk:
                                yield chunk + "\n"
                                if chunk.strip() == "data: [DONE]":
                                    break
                    except Exception as e:
                        logger.error(f"Stream error: {e}")
                    finally:
                        await resp.aclose()

                return StreamingResponse(stream(), media_type="text/event-stream")
            else:
                resp = await c.request(method, url, json=body, headers=headers)
                return Response(content=resp.content, status_code=resp.status_code,
                                media_type=resp.headers.get("content-type", "application/json"))
    except httpx.HTTPStatusError as e:
        return Response(content=e.response.content, status_code=e.response.status_code,
                        media_type=e.response.headers.get("content-type", "application/json"))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Upstream timeout")
    except Exception as e:
        logger.error(f"OpenAI proxy error: {e}")
        raise HTTPException(status_code=502, detail=str(e))


# ── Chat Completions ──────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="system, user, assistant, or tool")
    content: str | list | None = None

class ChatCompletionRequest(BaseModel):
    model: str = Field(default="gpt-4o-mini")
    messages: list[ChatMessage] = Field(..., min_length=1)
    stream: Optional[bool] = False
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: Optional[int] = None
    stop: Optional[str | list[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    user: Optional[str] = None


@router.post("/chat/completions", dependencies=[Depends(require_auth)])
async def chat_completions(body: ChatCompletionRequest, request: Request):
    return await _proxy("POST", "chat/completions", body.model_dump(exclude_none=True), request)


# ── Moderations ───────────────────────────────────────────────────────────

class ModerationInput(BaseModel):
    input: str | list[str] = Field(...)
    model: Optional[str] = None


@router.post("/moderations", dependencies=[Depends(require_auth)])
async def moderations(body: ModerationInput, request: Request):
    return await _proxy("POST", "moderations", body.model_dump(exclude_none=True), request)


# ── Embeddings ────────────────────────────────────────────────────────────

class EmbeddingInput(BaseModel):
    input: str | list[str] | list[int] | list[list[int]] = Field(...)
    model: str = Field(default="text-embedding-3-small")
    encoding_format: Optional[str] = None
    dimensions: Optional[int] = None
    user: Optional[str] = None


@router.post("/embeddings", dependencies=[Depends(require_auth)])
async def embeddings(body: EmbeddingInput, request: Request):
    return await _proxy("POST", "embeddings", body.model_dump(exclude_none=True), request)


# ── Images ────────────────────────────────────────────────────────────────

class ImageGenerationInput(BaseModel):
    prompt: str = Field(...)
    model: Optional[str] = None
    n: Optional[int] = None
    quality: Optional[str] = None
    response_format: Optional[str] = None
    size: Optional[str] = None
    style: Optional[str] = None
    user: Optional[str] = None


@router.post("/images/generations", dependencies=[Depends(require_auth)])
async def image_generations(body: ImageGenerationInput, request: Request):
    return await _proxy("POST", "images/generations", body.model_dump(exclude_none=True), request)


# ── Responses API ─────────────────────────────────────────────────────────

class ResponseInput(BaseModel):
    model: str = Field(default="gpt-4o-mini")
    input: str | list = Field(...)
    instructions: Optional[str] = None
    stream: Optional[bool] = False
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None
    tools: Optional[list] = None
    store: Optional[bool] = None
    metadata: Optional[dict] = None
    user: Optional[str] = None


@router.post("/responses", dependencies=[Depends(require_auth)])
async def responses_api(body: ResponseInput, request: Request):
    return await _proxy("POST", "responses", body.model_dump(exclude_none=True), request)


# ── Models list ───────────────────────────────────────────────────────────

@router.get("/models", dependencies=[Depends(require_auth)])
async def list_models(request: Request):
    return await _proxy("GET", "models", None, request)


@router.get("/models/{model_id}", dependencies=[Depends(require_auth)])
async def retrieve_model(model_id: str, request: Request):
    return await _proxy("GET", f"models/{model_id}", None, request)
