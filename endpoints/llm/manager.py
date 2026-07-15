"""Provider pool with retry, fallback, and speed-based ordering."""
import asyncio
import time
import logging
from typing import Generator

import tiktoken

from endpoints.llm.providers import PROVIDERS, ProviderInfo
from endpoints.llm import monitor

logger = logging.getLogger("api-proxy.llm")

_enc = tiktoken.get_encoding("cl100k_base")

# Build model → provider mapping
MODEL_MAP: dict[str, str] = {}
for _p in PROVIDERS:
    for _m in _p.available_models:
        MODEL_MAP[_m] = _p.name
        MODEL_MAP[_p.clean_names.get(_m, _m)] = _p.name


def _enabled_providers() -> list[ProviderInfo]:
    return [p for p in PROVIDERS if p.enabled and monitor.is_available(p.name)]


def get_provider_status():
    return monitor.get_all_stats()


def _count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def _build_params(provider: ProviderInfo, request, model: str, stream: bool) -> dict:
    """Build params dict for provider call, handling multimodal content."""
    messages = []
    for m in request.messages:
        msg: dict = {"role": m.role}
        if m.content is None:
            msg["content"] = None
        elif isinstance(m.content, str):
            msg["content"] = m.content
        elif isinstance(m.content, list):
            if provider.supports_images:
                msg["content"] = [
                    part.model_dump() if hasattr(part, "model_dump") else part
                    for part in m.content
                ]
            else:
                text_parts = []
                for part in m.content:
                    part_dict = part.model_dump() if hasattr(part, "model_dump") else part
                    if part_dict.get("type") == "text":
                        text_parts.append(part_dict["text"])
                    elif part_dict.get("type") == "image_url":
                        text_parts.append("[image]")
                    elif part_dict.get("type") == "file":
                        text_parts.append("[file]")
                msg["content"] = " ".join(text_parts) if text_parts else ""
        else:
            msg["content"] = str(m.content)
        messages.append(msg)

    params: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "stream": stream,
    }
    return {k: v for k, v in params.items() if v is not None}


def _get_sync_stream(provider: ProviderInfo, model: str, params: dict) -> Generator:
    """Get raw sync stream from provider."""
    client = provider.factory()
    return client.chat.completions.create(**params)


async def execute_chat(request):
    """Execute chat completion with retry/fallback.
    Returns (provider_name, response, is_stream).
    - If stream=True: response is a sync generator (yielded directly to client)
    - If stream=False: response is a dict with aggregated content
    """
    providers = _enabled_providers()
    if not providers:
        raise RuntimeError("No available providers (all disabled or on cooldown)")

    requested_model = request.model or "auto"

    # If specific model requested, try its provider first
    if requested_model != "auto":
        pname = MODEL_MAP.get(requested_model)
        if pname:
            for p in PROVIDERS:
                if p.name == pname and p.enabled:
                    result = await _try_provider(p, request)
                    if result is not None:
                        return result
                    break

    # Fallback: try all providers in priority order
    for provider in providers:
        result = await _try_provider(provider, request)
        if result is not None:
            return result

    raise RuntimeError("All providers failed")


async def _try_provider(provider: ProviderInfo, request):
    """Try a single provider. Returns (name, response, is_stream) or None."""
    model = provider.resolve_model(request.model)
    if not model:
        return None

    clean_name = provider.clean_names.get(model, model)

    try:
        start = time.time()
        params = _build_params(provider, request, model, stream=True)

        if request.stream:
            # Stream: get the sync generator, wrap it to track success at the end
            raw_stream = await asyncio.get_event_loop().run_in_executor(
                None, lambda: _get_sync_stream(provider, model, params)
            )
            latency = (time.time() - start) * 1000
            monitor.record_success(provider.name, clean_name, latency)
            return provider.name, raw_stream, True
        else:
            # Non-stream: aggregate internally, return dict
            full_text = ""
            finish_reason = None
            usage = None

            def _sync():
                nonlocal full_text, finish_reason, usage
                stream = _get_sync_stream(provider, model, params)
                for chunk in stream:
                    if hasattr(chunk, "choices") and chunk.choices:
                        choice = chunk.choices[0]
                        delta = getattr(choice, "delta", None)
                        if delta:
                            full_text += getattr(delta, "content", "") or ""
                        fr = getattr(choice, "finish_reason", None)
                        if fr:
                            finish_reason = fr
                    if hasattr(chunk, "usage") and chunk.usage:
                        usage = chunk.usage

            await asyncio.get_event_loop().run_in_executor(None, _sync)
            latency = (time.time() - start) * 1000

            if not full_text or full_text.strip() == "":
                monitor.record_error(provider.name, clean_name, "empty response")
                logger.info(f"Provider {provider.name}/{clean_name}: empty response")
                return None

            # Count tokens if provider didn't return usage
            if not usage:
                prompt_text = " ".join(
                    m.get("content", "") for m in (request.messages or [])
                    if isinstance(m.get("content"), str)
                )
                prompt_tokens = _count_tokens(prompt_text)
                completion_tokens = _count_tokens(full_text)
                usage = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                }

            monitor.record_success(provider.name, clean_name, latency)
            return provider.name, {
                "content": full_text,
                "finish_reason": finish_reason or "stop",
                "usage": usage,
                "model": model,
            }, False

    except Exception as e:
        monitor.record_error(provider.name, clean_name, str(e))
        logger.info(f"Provider {provider.name}/{clean_name} failed: {e}")
        return None
