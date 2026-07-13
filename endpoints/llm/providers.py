"""Free LLM provider registry with benchmark data."""
import os
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ProviderInfo:
    name: str
    factory: Callable[..., Any]
    available_models: list[str]
    supports_stream: bool = True
    requires_auth: bool = False
    priority: int = 0
    enabled: bool = True


def _get_pollinations(model="llama"):
    from endpoints.llm.pollinations_provider import PollinationsClient
    return PollinationsClient(model=model)


def _get_pollinations_fn(model_name):
    def _factory():
        from endpoints.llm.pollinations_provider import PollinationsClient
        return PollinationsClient(model=model_name)
    return _factory


def _get_heckai():
    from llm4free import HeckAI
    return HeckAI()


# Pollinations models sorted by benchmark speed (ms):
# llama(414) gemma(445) deepseek(466) openai(520) mistral(788)
# mistral-small(1063) grok(1415) qwen-coder(1528) nova-fast(1945) nova(2931)
# Plus HeckAI (free, no auth) as ultimate fallback

PROVIDERS: list[ProviderInfo] = [
    ProviderInfo("poll-llama", _get_pollinations_fn("llama"), ["llama"], priority=0),
    ProviderInfo("poll-gemma", _get_pollinations_fn("gemma"), ["gemma"], priority=1),
    ProviderInfo("poll-deepseek", _get_pollinations_fn("deepseek"), ["deepseek"], priority=2),
    ProviderInfo("poll-openai", _get_pollinations_fn("openai"), ["openai"], priority=3),
    ProviderInfo("poll-mistral", _get_pollinations_fn("mistral"), ["mistral"], priority=4),
    ProviderInfo("poll-mistral-small", _get_pollinations_fn("mistral-small-3.2"), ["mistral-small-3.2"], priority=5),
    ProviderInfo("poll-grok", _get_pollinations_fn("grok"), ["grok"], priority=6),
    ProviderInfo("poll-qwen-coder", _get_pollinations_fn("qwen-coder"), ["qwen-coder"], priority=7),
    ProviderInfo("poll-nova-fast", _get_pollinations_fn("nova-fast"), ["nova-fast"], priority=8),
    ProviderInfo("poll-nova", _get_pollinations_fn("nova"), ["nova"], priority=9),
    ProviderInfo("heckai", _get_heckai, ["deepseek/deepseek-v4-flash"], priority=10),
]


def get_provider_by_name(name: str) -> ProviderInfo | None:
    for p in PROVIDERS:
        if p.name == name:
            return p
    return None
