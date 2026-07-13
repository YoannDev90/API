"""Provider pool with retry, fallback, and speed-based ordering."""
import asyncio
import time
import logging

from endpoints.llm.providers import PROVIDERS, ProviderInfo
from endpoints.llm import monitor

logger = logging.getLogger("api-proxy.llm")

FREE_MODEL_DEFAULTS = [
    "qwen7b",
    "standard",
    "MBZUAI-IFM/K2-Think-v2",
    "gpt-4o",
    "deepseek/deepseek-v4-flash",
]


def _resolve_model(provider: ProviderInfo, requested: str) -> str:
    if requested and requested != "auto":
        return requested
    if provider.available_models:
        return provider.available_models[0]
    return FREE_MODEL_DEFAULTS[0]


def _enabled_providers() -> list[ProviderInfo]:
    enabled = [p for p in PROVIDERS if p.enabled and monitor.is_available(p.name)]
    enabled.sort(key=lambda p: (monitor.avg_latency(p.name), -p.priority))
    return enabled


def get_provider_status():
    return monitor.get_all_stats()


async def execute_chat(request):
    """Execute chat completion with retry/fallback across providers.
    Returns (provider_name, response, is_stream).
    """
    providers = _enabled_providers()
    if not providers:
        raise RuntimeError("No available providers (all disabled or on cooldown)")

    errors = []
    for provider in providers:
        model = _resolve_model(provider, request.model)
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
                    errors.append(f"{provider.name}: empty response")
                    continue

                monitor.record_success(provider.name, latency)
                return provider.name, response, False
        except Exception as e:
            monitor.record_error(provider.name)
            errors.append(f"{provider.name}: {e}")
            logger.info(f"Provider {provider.name} failed: {e}")
            continue

    summary = "; ".join(errors)
    raise RuntimeError(f"All {len(providers)} providers failed: {summary}")


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
