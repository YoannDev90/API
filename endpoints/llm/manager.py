"""Provider pool with retry, fallback, and speed-based ordering."""
import asyncio
import time
import logging
from collections import defaultdict

from endpoints.llm.providers import PROVIDERS, ProviderInfo

logger = logging.getLogger("api-proxy.llm")

_metrics: dict[str, dict] = defaultdict(lambda: {"latencies": [], "errors": 0, "successes": 0, "consecutive_errors": 0})
_cooldown_until: dict[str, float] = {}
_COOLDOWN_SECONDS = 60
_MAX_ERRORS = 5
_WINDOW = 20

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


def _avg_latency(name: str) -> float:
    lats = _metrics[name]["latencies"][-_WINDOW:]
    return sum(lats) / len(lats) if lats else 999.0


def _enabled_providers() -> list[ProviderInfo]:
    now = time.time()
    enabled = []
    for p in PROVIDERS:
        if not p.enabled:
            continue
        if _cooldown_until.get(p.name, 0) > now:
            continue
        enabled.append(p)
    enabled.sort(key=lambda p: (_avg_latency(p.name), -p.priority))
    return enabled


def _record_success(name: str, latency_ms: float):
    _metrics[name]["successes"] += 1
    _metrics[name]["latencies"].append(latency_ms)
    _metrics[name]["consecutive_errors"] = 0
    if len(_metrics[name]["latencies"]) > _WINDOW * 5:
        _metrics[name]["latencies"] = _metrics[name]["latencies"][-_WINDOW:]


def _record_error(name: str):
    _metrics[name]["errors"] += 1
    _metrics[name]["consecutive_errors"] += 1
    if _metrics[name]["consecutive_errors"] >= _MAX_ERRORS:
        _cooldown_until[name] = time.time() + _COOLDOWN_SECONDS
        logger.warning(f"Provider {name} on cooldown ({_MAX_ERRORS} consecutive errors)")


def get_provider_status():
    from endpoints.llm.models import ProviderStatus
    results = []
    for p in PROVIDERS:
        m = _metrics[p.name]
        results.append(ProviderStatus(
            name=p.name, enabled=p.enabled,
            latency_ms=round(_avg_latency(p.name), 1),
            successes=m["successes"], errors=m["errors"],
            available_models=p.available_models,
            supports_stream=p.supports_stream,
        ))
    return sorted(results, key=lambda x: (-x.successes, x.latency_ms))


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
                _record_success(provider.name, latency)
                return provider.name, response, True
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda m=model, p=provider: _call_sync(p, request, m)
                )
                latency = (time.time() - start) * 1000

                # Check if response has actual content
                choice = response.choices[0] if response.choices else None
                content = choice.message.content if choice and choice.message else None
                if not content or content.strip() == "":
                    _record_error(provider.name)
                    errors.append(f"{provider.name}: empty response")
                    logger.info(f"Provider {provider.name}: empty response")
                    continue

                _record_success(provider.name, latency)
                return provider.name, response, False
        except Exception as e:
            _record_error(provider.name)
            errors.append(f"{provider.name}: {e}")
            logger.info(f"Provider {provider.name} failed: {e}")
            continue

    summary = "; ".join(errors)
    raise RuntimeError(f"All {len(providers)} providers failed: {summary}")


def _call_sync(provider, request, model: str):
    """Synchronous call to a provider."""
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
    """Stream call to a provider. Returns an async generator of OpenAI SSE chunks."""
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
