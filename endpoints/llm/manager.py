"""Provider pool with retry, fallback, and speed-based ordering."""
import asyncio
import time
import logging

from endpoints.llm.providers import PROVIDERS, ProviderInfo
from endpoints.llm import monitor

logger = logging.getLogger("api-proxy.llm")

# Build model → provider mapping from benchmark data
MODEL_MAP: dict[str, str] = {}
for _p in PROVIDERS:
    for _m in _p.available_models:
        MODEL_MAP[_m] = _p.name


def _resolve_model(provider: ProviderInfo, requested: str) -> str:
    if requested and requested != "auto":
        if requested in provider.available_models:
            return requested
        return provider.available_models[0] if provider.available_models else None
    return provider.available_models[0] if provider.available_models else None


def _get_provider_for_model(model_name: str) -> ProviderInfo | None:
    """Find the best provider for a specific model name."""
    pname = MODEL_MAP.get(model_name)
    if pname:
        for p in PROVIDERS:
            if p.name == pname and p.enabled and monitor.is_available(p.name):
                return p
    return None


def _enabled_providers() -> list[ProviderInfo]:
    return [p for p in PROVIDERS if p.enabled and monitor.is_available(p.name)]


def get_provider_status():
    return monitor.get_all_stats()


async def execute_chat(request):
    """Execute chat completion with retry/fallback.
    Returns (provider_name, response, is_stream).
    """
    providers = _enabled_providers()
    if not providers:
        raise RuntimeError("No available providers (all disabled or on cooldown)")

    # If specific model requested, try its provider first (even if on cooldown)
    if request.model and request.model != "auto":
        pname = MODEL_MAP.get(request.model)
        if pname:
            for p in PROVIDERS:
                if p.name == pname and p.enabled:
                    result = await _try_provider(p, request)
                    if result is not None:
                        return result
                    break

    # Fallback: try all providers in speed order
    for provider in providers:
        result = await _try_provider(provider, request)
        if result is not None:
            return result

    raise RuntimeError("All providers failed")


async def _try_provider(provider: ProviderInfo, request):
    """Try a single provider. Returns (name, response, is_stream) or None."""
    model = _resolve_model(provider, request.model)
    if not model:
        return None

    try:
        start = time.time()
        if request.stream:
            response = await _call_stream(provider, request, model)
            latency = (time.time() - start) * 1000
            monitor.record_success(provider.name, latency)
            return provider.name, response, True
        else:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda m=model, p=provider: _call_sync(p, request, m)
            )
            latency = (time.time() - start) * 1000

            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice and choice.message else None
            if not content or content.strip() == "":
                monitor.record_error(provider.name)
                logger.info(f"Provider {provider.name}: empty response")
                return None

            monitor.record_success(provider.name, latency)
            return provider.name, response, False
    except Exception as e:
        monitor.record_error(provider.name)
        logger.info(f"Provider {provider.name} failed: {e}")
        return None


def _call_sync(provider, request, model: str):
    client = provider.factory()
    params = {
        "model": model,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "stream": False,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return client.chat.completions.create(**params)


async def _call_stream(provider, request, model: str):
    client = provider.factory()
    params = {
        "model": model,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "stream": True,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: client.chat.completions.create(**params)
    )
