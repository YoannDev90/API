"""Free LLM provider registry."""
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ProviderInfo:
    name: str
    factory: Callable[..., Any]
    available_models: list[str]
    supports_stream: bool = True
    requires_auth: bool = False
    priority: int = 0  # lower = higher priority
    latency_ms: float = 0.0  # tracked at runtime
    errors: int = 0
    successes: int = 0
    enabled: bool = True


def _get_heckai():
    from llm4free import HeckAI
    return HeckAI()


def _get_artingai():
    from llm4free import ArtingAI
    return ArtingAI()


def _get_freeai():
    from llm4free import FreeAI
    return FreeAI()


def _get_chatgpt():
    from llm4free import ChatGPT
    return ChatGPT()


def _get_gptfree():
    from llm4free import GptFree
    return GptFree()


def _get_freeai_online():
    from llm4free import FreeAIOnline
    return FreeAIOnline()


def _get_essai():
    from llm4free import EssentialAI
    return EssentialAI()


def _get_k2think():
    from llm4free import K2Think
    return K2Think()


PROVIDERS: list[ProviderInfo] = [
    ProviderInfo("heckai", _get_heckai, ["deepseek/deepseek-v4-flash", "openai/gpt-5.4-mini", "google/gemini-3-flash-preview"], priority=0),
    ProviderInfo("freeai", _get_freeai, ["gpt-4o-mini"], priority=1),
    ProviderInfo("chatgpt", _get_chatgpt, ["gpt-4o-mini"], priority=2),
    ProviderInfo("gptfree", _get_gptfree, ["gpt-4o-mini"], priority=3),
    ProviderInfo("freeai_online", _get_freeai_online, [], priority=4),
    ProviderInfo("essai", _get_essai, [], priority=5),
    ProviderInfo("k2think", _get_k2think, [], priority=6),
    ProviderInfo("artingai", _get_artingai, ["gpt-5", "gpt-4o-mini"], priority=7),
]


def get_provider_by_name(name: str) -> ProviderInfo | None:
    for p in PROVIDERS:
        if p.name == name:
            return p
    return None
