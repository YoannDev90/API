"""Free LLM API routes (OpenAI-compatible)."""
import json
import time
import logging
import uuid
from logging import getLogger

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse

from endpoints.llm.models import ChatCompletionRequest, EmbeddingRequest, ModelListResponse
from endpoints.llm import manager
from endpoints.llm.providers import PROVIDERS

logger = logging.getLogger("api-proxy.llm")
router = APIRouter(prefix="/v1", tags=["free-llm"])


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Chat completion with auto-fallback across free providers."""
    try:
        provider_name, response, is_stream = await manager.execute_chat(request)
        if is_stream:
            return _stream_response(response, provider_name)
        return _sync_response(response, provider_name, request)
    except RuntimeError as e:
        return JSONResponse(
            status_code=502,
            content={"error": {"message": str(e), "type": "server_error", "code": "all_providers_failed"}},
        )


def _sync_response(response, provider: str, request: ChatCompletionRequest):
    """Convert provider response to OpenAI-compatible JSON."""
    choice = response.choices[0]
    usage = getattr(response, "usage", None)
    return JSONResponse({
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": getattr(response, "model", request.model),
        "provider": provider,
        "choices": [{
            "index": 0,
            "message": {
                "role": getattr(choice.message, "role", "assistant"),
                "content": choice.message.content,
            },
            "finish_reason": getattr(choice, "finish_reason", "stop"),
        }],
        "usage": {
            "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
            "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
            "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0,
        } if usage else None,
    })


def _stream_response(stream, provider: str):
    """Convert streaming response to SSE format."""
    async def generate():
        try:
            for chunk in stream:
                if hasattr(chunk, "choices") and chunk.choices:
                    choice = chunk.choices[0]
                    delta = getattr(choice, "delta", None)
                    content = getattr(delta, "content", None) if delta else None
                    finish = getattr(choice, "finish_reason", None)
                    chunk_data = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "provider": provider,
                        "choices": [{
                            "index": 0,
                            "delta": {"role": "assistant"} if content is None and finish is None else {"content": content},
                            "finish_reason": finish,
                        }],
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                if hasattr(chunk, "choices") and chunk.choices and getattr(chunk.choices[0], "finish_reason", None):
                    break
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/embeddings")
async def embeddings(request: EmbeddingRequest):
    """Basic embeddings endpoint (placeholder)."""
    return {"code": "501", "detail": "Embeddings not yet implemented for free providers"}


@router.get("/models")
async def list_models():
    """List all available free models."""
    all_models = []
    for p in PROVIDERS:
        for m in p.available_models:
            all_models.append({
                "id": m,
                "object": "model",
                "created": 0,
                "owned_by": p.name,
                "permission": [],
                "root": m,
            })
    if not all_models:
        # List known free models directly
        known = [
            "deepseek/deepseek-v4-flash", "deepseek/deepseek-v4-pro",
            "qwen/qwen3.7-plus", "stepfun/step-3.7-flash",
            "google/gemini-3.1-flash-lite", "google/gemini-3-flash-preview",
            "openai/gpt-5.4-mini", "minimax/minimax-m3",
        ]
        for m in known:
            all_models.append({"id": m, "object": "model", "created": 0, "owned_by": "free"})
    return ModelListResponse(object="list", data=all_models)


@router.get("/providers")
async def list_providers():
    """List providers with their status and performance metrics."""
    return {"providers": manager.get_provider_status()}


@router.post("/providers/{name}/toggle")
async def toggle_provider(name: str, enabled: bool = Query(default=True)):
    """Enable or disable a provider."""
    from endpoints.llm.providers import get_provider_by_name
    p = get_provider_by_name(name)
    if not p:
        raise HTTPException(status_code=404, detail=f"Provider {name} not found")
    p.enabled = enabled
    return {"name": name, "enabled": enabled}
