"""LLM monitor: baseline tests + per-provider and per-model stats."""
import asyncio
import time
import json
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger("api-proxy.llm")

_INTERVAL = 600
_WINDOW = 50
_COOLDOWN_SECONDS = 300

_provider_metrics: dict[str, dict] = defaultdict(lambda: {
    "latencies": [], "successes": 0, "errors": 0,
    "last_test": 0, "consecutive_errors": 0,
})

_model_metrics: dict[str, dict] = defaultdict(lambda: {
    "successes": 0, "errors": 0, "latencies": [],
    "last_success": 0, "last_error": 0, "last_error_msg": "",
})

_cooldown_until: dict[str, float] = {}
_background_started = False


def record_success(provider: str, model: str, latency_ms: float):
    # Provider stats
    m = _provider_metrics[provider]
    m["successes"] += 1
    m["latencies"].append(latency_ms)
    m["consecutive_errors"] = 0
    if len(m["latencies"]) > _WINDOW:
        m["latencies"] = m["latencies"][-_WINDOW:]

    # Model stats
    mm = _model_metrics[model]
    mm["successes"] += 1
    mm["latencies"].append(latency_ms)
    mm["last_success"] = time.time()
    if len(mm["latencies"]) > _WINDOW:
        mm["latencies"] = mm["latencies"][-_WINDOW:]


def record_error(provider: str, model: str = "", error_msg: str = ""):
    m = _provider_metrics[provider]
    m["errors"] += 1
    m["consecutive_errors"] += 1
    if m["consecutive_errors"] >= 5:
        _cooldown_until[provider] = time.time() + _COOLDOWN_SECONDS
        logger.warning(f"Provider {provider} on cooldown")

    if model:
        mm = _model_metrics[model]
        mm["errors"] += 1
        mm["last_error"] = time.time()
        mm["last_error_msg"] = error_msg[:200]


def is_available(provider: str) -> bool:
    return _cooldown_until.get(provider, 0) <= time.time()


def avg_latency(provider: str) -> float:
    lats = _provider_metrics[provider]["latencies"][-_WINDOW:]
    return sum(lats) / len(lats) if lats else 999.0


def success_rate(provider: str) -> float:
    m = _provider_metrics[provider]
    total = m["successes"] + m["errors"]
    return (m["successes"] / total * 100) if total > 0 else 0.0


def get_all_stats() -> list[dict]:
    from endpoints.llm.providers import PROVIDERS
    results = []
    for p in PROVIDERS:
        m = _provider_metrics[p.name]
        total = m["successes"] + m["errors"]
        results.append({
            "name": p.name,
            "enabled": p.enabled and is_available(p.name),
            "success_rate": round(success_rate(p.name), 1),
            "latency_ms": round(avg_latency(p.name)),
            "successes": m["successes"],
            "errors": m["errors"],
            "total_requests": total,
            "last_test": m["last_test"],
        })
    return sorted(results, key=lambda x: (-x["success_rate"], x["latency_ms"]))


def get_model_stats() -> list[dict]:
    """Get stats for all tracked models."""
    results = []
    for model, m in _model_metrics.items():
        total = m["successes"] + m["errors"]
        avg_lat = sum(m["latencies"][-_WINDOW:]) / len(m["latencies"][-_WINDOW:]) if m["latencies"] else 0
        results.append({
            "model": model,
            "successes": m["successes"],
            "errors": m["errors"],
            "total_requests": total,
            "success_rate": round((m["successes"] / total * 100) if total > 0 else 0, 1),
            "avg_latency_ms": round(avg_lat),
            "last_success": m["last_success"],
            "last_error": m["last_error"],
            "last_error_msg": m["last_error_msg"],
        })
    return sorted(results, key=lambda x: (-x["success_rate"], x["total_requests"]))


async def baseline_test():
    """Run one baseline test per enabled provider when idle."""
    from endpoints.llm.manager import _enabled_providers, _get_sync_stream, _build_params
    for provider in _enabled_providers():
        if time.time() - _provider_metrics[provider.name]["last_test"] < _INTERVAL:
            continue
        try:
            model = provider.available_models[0] if provider.available_models else None
            if not model:
                _provider_metrics[provider.name]["last_test"] = time.time()
                return

            from endpoints.llm.models import ChatCompletionRequest
            req = ChatCompletionRequest(
                model=model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10,
            )
            params = _build_params(provider, req, model, stream=True)

            start = time.time()
            def _sync():
                stream = _get_sync_stream(provider, model, params)
                for chunk in stream:
                    pass  # consume stream
            await asyncio.get_event_loop().run_in_executor(None, _sync)
            latency = (time.time() - start) * 1000

            _provider_metrics[provider.name]["last_test"] = time.time()
            record_success(provider.name, model, latency)
            logger.info(f"Baseline {provider.name}/{model}: {latency:.0f}ms")
        except Exception as e:
            _provider_metrics[provider.name]["last_test"] = time.time()
            record_error(provider.name, model, str(e))
            logger.info(f"Baseline {provider.name} failed: {e}")


async def _monitor_loop():
    while True:
        try:
            await baseline_test()
        except Exception as e:
            logger.error(f"Monitor error: {e}")
        await asyncio.sleep(_INTERVAL)


def start_monitor():
    global _background_started
    if _background_started:
        return
    _background_started = True
    asyncio.ensure_future(_monitor_loop())
    logger.info(f"Monitor started: baseline tests every {_INTERVAL}s")
