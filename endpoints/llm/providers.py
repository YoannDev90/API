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
    from llm4free import FreeAI; return FreeAI()

def _get_deepai():
    from llm4free import DeepAI; return DeepAI()

def _get_freeai_online():
    from llm4free import FreeAIOnline; return FreeAIOnline()

def _get_netwrck():
    from llm4free import Netwrck; return Netwrck()

def _get_ai4chat():
    from llm4free import AI4Chat; return AI4Chat()

def _get_heckai():
    from llm4free import HeckAI; return HeckAI()

# Providers: 42 verified models from full benchmark
PROVIDERS: list[ProviderInfo] = [
    ProviderInfo("freeai", _get_freeai, ["qwen3-8b", "qwen7b"], priority=0),
    ProviderInfo("deepai", _get_deepai, [
        "gpt-oss-120b", "gemini-2.5-flash-lite", "llama-4-scout",
        "llama-3.3-70b-instruct", "deepseek-v3.2", "llama-3.1-8b-instant",
        "gemini-3-pro", "gpt-4.1-nano", "qwen3-30b", "gpt-5-nano",
        "gemma-3-12b", "gemini2-9b", "standard",
    ], priority=1),
    ProviderInfo("freeai_online", _get_freeai_online, ["gpt-4o"], priority=2),
    ProviderInfo("netwrck", _get_netwrck, [
        "nvidia/llama-3.1-nemotron-70b-instruct", "deepseek/deepseek-chat",
        "minimax/minimax-m2.5",
    ], priority=3),
    ProviderInfo("ai4chat", _get_ai4chat, [
        "codex-mini", "o1-pro", "o4-mini", "grok-4.1-fast",
        "gemini-3-flash", "gpt-4.1-nano", "gpt-3.5", "o3-mini-high",
        "o3-mini", "gpt-5.2", "gpt-4.5", "gpt-4o-mini-search-preview",
    ], priority=4),
    ProviderInfo("heckai", _get_heckai, [
        "google/gemini-3.1-flash-lite", "google/gemini-3-flash-preview",
        "openai/gpt-5.4-mini", "minimax/minimax-m3",
        "deepseek/deepseek-v4-flash", "deepseek/deepseek-v4-pro",
        "stepfun/step-3.7-flash", "tencent/hy3-preview",
        "qwen/qwen3.7-plus",
    ], priority=5),
]


def get_provider_by_name(name: str) -> ProviderInfo | None:
    for p in PROVIDERS:
        if p.name == name:
            return p
    return None
