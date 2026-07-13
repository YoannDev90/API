"""LLM monitor: baseline tests (5 req/hour) + real user measurements."""
import asyncio
import time
import json
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger("api-proxy.llm")

_INTERVAL = 600  # test every 10 minutes
_WINDOW = 50
_COOLDOWN_SECONDS = 300

_metrics: dict[str, dict] = defaultdict(lambda: {
    "latencies": [], "successes": 0, "errors": 0,
    "last_test": 0, "consecutive_errors": 0, "active": True,
})
_cooldown_until: dict[str, float] = {}
_background_started = False


def record_success(provider: str, latency_ms: float):
    m = _metrics[provider]
    m["successes"] += 1
    m["latencies"].append(latency_ms)
    m["consecutive_errors"] = 0
    if len(m["latencies"]) > _WINDOW:
        m["latencies"] = m["latencies"][-_WINDOW:]


def record_error(provider: str):
    m = _metrics[provider]
    m["errors"] += 1
    m["consecutive_errors"] += 1
    if m["consecutive_errors"] >= 5:
        _cooldown_until[provider] = time.time() + _COOLDOWN_SECONDS
        logger.warning(f"Provider {provider} on cooldown")


def is_available(provider: str) -> bool:
    return _cooldown_until.get(provider, 0) <= time.time()


def avg_latency(provider: str) -> float:
    lats = _metrics[provider]["latencies"][-_WINDOW:]
    return sum(lats) / len(lats) if lats else 999.0


def success_rate(provider: str) -> float:
    m = _metrics[provider]
    total = m["successes"] + m["errors"]
    return (m["successes"] / total * 100) if total > 0 else 0.0


def get_all_stats() -> list[dict]:
    from endpoints.llm.providers import PROVIDERS
    results = []
    for p in PROVIDERS:
        m = _metrics[p.name]
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


async def baseline_test():
    """Run one baseline test per enabled provider when idle."""
    from endpoints.llm.manager import _enabled_providers
    for provider in _enabled_providers():
        if time.time() - _metrics[provider.name]["last_test"] < _INTERVAL:
            continue
        try:
            from endpoints.llm.manager import _call_sync
            from endpoints.llm.models import ChatCompletionRequest
            req = ChatCompletionRequest(
                model=provider.available_models[0] if provider.available_models else "auto",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10,
            )
            start = time.time()
            await asyncio.get_event_loop().run_in_executor(
                None, lambda p=provider: _call_sync(p, req, provider.available_models[0] if provider.available_models else None)
            )
            latency = (time.time() - start) * 1000
            _metrics[provider.name]["last_test"] = time.time()
            record_success(provider.name, latency)
            logger.info(f"Baseline {provider.name}: {latency:.0f}ms")
        except Exception as e:
            _metrics[provider.name]["last_test"] = time.time()
            record_error(provider.name)
            logger.info(f"Baseline {provider.name} failed: {e}")


async def _monitor_loop():
    """Background loop: run baseline tests periodically."""
    while True:
        try:
            await baseline_test()
        except Exception as e:
            logger.error(f"Monitor error: {e}")
        await asyncio.sleep(_INTERVAL)


def start_monitor():
    """Start the background monitor. Call once at startup."""
    global _background_started
    if _background_started:
        return
    _background_started = True
    asyncio.ensure_future(_monitor_loop())
    logger.info(f"Monitor started: baseline tests every {_INTERVAL}s")
