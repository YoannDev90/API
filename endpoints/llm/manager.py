"""Provider pool with retry, fallback, and speed-based ordering."""
import asyncio
import time
import logging
from collections import defaultdict
from dataclasses import dataclass

from endpoints.llm.providers import PROVIDERS, ProviderInfo

logger = logging.getLogger("api-proxy.llm")

# Track per-provider metrics: {provider_name: {"latencies": [...], "errors": int, "successes": int}}
_metrics: dict[str, dict] = defaultdict(lambda: {"latencies": [], "errors": 0, "successes": 0, "consecutive_errors": 0})
_cooldown_until: dict[str, float] = {}
_COOLDOWN_SECONDS = 60
_MAX_ERRORS = 5
_WINDOW = 20  # last N requests for avg


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
        raise RuntimeError("No available providers")

    last_error = None
    for provider in providers:
        try:
            start = time.time()
            if request.stream:
                response = await _call_stream(provider, request)
                latency = (time.time() - start) * 1000
                _record_success(provider.name, latency)
                return provider.name, response, True
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: _call_sync(provider, request)
                )
                latency = (time.time() - start) * 1000
                _record_success(provider.name, latency)
                return provider.name, response, False
        except Exception as e:
            _record_error(provider.name)
            last_error = e
            logger.info(f"Provider {provider.name} failed: {e}")
            continue

    raise RuntimeError(f"All providers failed. Last error: {last_error}")


def _call_sync(provider, request):
    """Synchronous call to a provider."""
    client = provider.factory()
    params = {
        "model": request.model if request.model != "auto" else None,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "stream": False,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return client.chat.completions.create(**params)


async def _call_stream(provider, request):
    """Stream call to a provider. Returns an async generator of OpenAI SSE chunks."""
    client = provider.factory()
    params = {
        "model": request.model if request.model != "auto" else None,
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "stream": True,
    }
    params = {k: v for k, v in params.items() if v is not None}

    stream = await asyncio.get_event_loop().run_in_executor(
        None, lambda: client.chat.completions.create(**params)
    )
    return stream
