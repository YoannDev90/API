"""Free LLM provider registry with benchmark data."""
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


def _get_freeai():
    from llm4free import FreeAI
    return FreeAI()


def _get_deepai():
    from llm4free import DeepAI
    return DeepAI()


def _get_k2think():
    from llm4free import K2Think
    return K2Think()


def _get_freeai_online():
    from llm4free import FreeAIOnline
    return FreeAIOnline()


def _get_netwrck():
    from llm4free import Netwrck
    return Netwrck()


def _get_wise_cat():
    from llm4free import WiseCat
    return WiseCat()


def _get_ai4chat():
    from llm4free import AI4Chat
    return AI4Chat()


def _get_heckai():
    from llm4free import HeckAI
    return HeckAI()


# Benchmark results:
# freeai (1589ms) → deepai (2469ms) → k2think (3057ms)
# → freeai_online (3158ms) → netwrck (3284ms) → wise_cat (3893ms)
# → ai4chat (5345ms) → heckai (5391ms)
PROVIDERS: list[ProviderInfo] = [
    ProviderInfo("freeai", _get_freeai, [], priority=0),
    ProviderInfo("deepai", _get_deepai, [], priority=1),
    ProviderInfo("k2think", _get_k2think, [], priority=2),
    ProviderInfo("freeai_online", _get_freeai_online, [], priority=3),
    ProviderInfo("netwrck", _get_netwrck, [], priority=4),
    ProviderInfo("wise_cat", _get_wise_cat, [], priority=5),
    ProviderInfo("ai4chat", _get_ai4chat, [], priority=6),
    ProviderInfo("heckai", _get_heckai, [], priority=7),
]


def get_provider_by_name(name: str) -> ProviderInfo | None:
    for p in PROVIDERS:
        if p.name == name:
            return p
    return None
