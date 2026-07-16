"""Free LLM provider registry with benchmark data."""
from dataclasses import dataclass, field
from typing import Any, Callable


def _clean_model_name(name: str) -> str:
    """Strip provider prefix from model name: 'stepfun/step-3.7-flash' → 'step-3.7-flash'."""
    if "/" in name:
        return name.split("/", 1)[1]
    return name



@dataclass
class ProviderInfo:
    name: str
    factory: Callable[..., Any]
    available_models: list[str]
    supports_stream: bool = True
    supports_images: bool = False
    supports_files: bool = False
    requires_auth: bool = False
    priority: int = 0
    enabled: bool = True
    clean_names: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.clean_names = {m: _clean_model_name(m) for m in self.available_models}

    def resolve_model(self, requested: str) -> str | None:
        """Resolve a model name (clean or original) to the original provider model name."""
        if not requested or requested == "auto":
            return self.available_models[0] if self.available_models else None
        if requested in self.available_models:
            return requested
        for orig, clean in self.clean_names.items():
            if clean == requested:
                return orig
        return None


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


PROVIDERS: list[ProviderInfo] = [
    ProviderInfo("freeai", _get_freeai, ["qwen3-8b", "qwen7b"], priority=0, enabled=False),
    ProviderInfo("deepai", _get_deepai, [
        "gpt-oss-120b", "gemini-2.5-flash-lite", "llama-4-scout",
        "llama-3.3-70b-instruct", "deepseek-v3.2", "llama-3.1-8b-instant",
        "gemini-3-pro", "gpt-4.1-nano", "qwen3-30b", "gpt-5-nano",
        "gemma-3-12b", "gemma2-9b", "standard", "super-genius",
    ], priority=1),
    ProviderInfo("freeai_online", _get_freeai_online, ["gpt-4o"], priority=2, enabled=False),
    ProviderInfo("netwrck", _get_netwrck, [
        "nvidia/llama-3.1-nemotron-70b-instruct", "deepseek/deepseek-chat",
        "minimax/minimax-m2.5",
    ], priority=3, enabled=False),
    ProviderInfo("ai4chat", _get_ai4chat, [
        "codex-mini", "o1-pro", "o4-mini", "grok-4.1-fast",
        "gemini-3-flash", "gpt-4.1-nano", "gpt-3.5", "o3-mini-high",
        "o3-mini", "gpt-5.2", "gpt-4.5", "gpt-4o-mini-search-preview",
    ], priority=4, enabled=False),
]

# Reverse lookup: clean_name → provider_name
CLEAN_NAME_MAP: dict[str, str] = {}
for _p in PROVIDERS:
    for _orig, _clean in _p.clean_names.items():
        CLEAN_NAME_MAP[_clean] = _p.name


def get_provider_by_name(name: str) -> ProviderInfo | None:
    for p in PROVIDERS:
        if p.name == name:
            return p
    return None


def resolve_provider_for_model(model_name: str) -> tuple[ProviderInfo, str] | None:
    """Resolve a model name (clean or original) to (provider, original_model)."""
    for p in PROVIDERS:
        resolved = p.resolve_model(model_name)
        if resolved:
            return p, resolved
    return None
