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


@router.on_event("startup")
async def _start_monitor():
    from endpoints.llm.monitor import start_monitor
    start_monitor()


@router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Chat completion with auto-fallback across free providers."""
    try:
        provider_name, result, is_stream = await manager.execute_chat(request)
        if is_stream:
            return _stream_response(result, provider_name, request.model)
        return _json_response(result, provider_name, request.model)
    except RuntimeError as e:
        return JSONResponse(
            status_code=502,
            content={"error": {"message": str(e), "type": "server_error", "code": "all_providers_failed"}},
        )


def _json_response(result: dict, provider: str, requested_model: str) -> JSONResponse:
    """Convert aggregated result to OpenAI-compatible JSON."""
    usage = result.get("usage")
    usage_dict = None
    if usage:
        if isinstance(usage, dict):
            usage_dict = usage
        elif hasattr(usage, "model_dump"):
            usage_dict = usage.model_dump()
        else:
            usage_dict = {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }

    return JSONResponse({
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": result.get("model", requested_model),
        "provider": provider,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": result["content"],
            },
            "finish_reason": result.get("finish_reason", "stop"),
        }],
        "usage": usage_dict,
    })


def _stream_response(raw_stream, provider: str, requested_model: str):
    """Yield SSE chunks directly from the provider's stream."""
    async def generate():
        try:
            for chunk in raw_stream:
                if not hasattr(chunk, "choices") or not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta = getattr(choice, "delta", None)
                content = getattr(delta, "content", None) if delta else None
                finish = getattr(choice, "finish_reason", None)

                chunk_data = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": getattr(chunk, "model", requested_model),
                    "provider": provider,
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant"} if content is None and finish is None else {"content": content},
                        "finish_reason": finish,
                    }],
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                if finish:
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
    """List all available free models with clean names."""
    all_models = []
    seen = set()
    for p in PROVIDERS:
        for m in p.available_models:
            clean = p.clean_names.get(m, m)
            if clean in seen:
                continue
            seen.add(clean)
            all_models.append({
                "id": clean,
                "object": "model",
                "created": 0,
                "owned_by": p.name,
                "original_id": m,
                "permission": [],
                "root": clean,
            })
    return ModelListResponse(object="list", data=all_models)


@router.get("/models/stats")
async def model_stats():
    """Get success/failure stats per model."""
    from endpoints.llm.monitor import get_model_stats
    return {"models": get_model_stats()}


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
