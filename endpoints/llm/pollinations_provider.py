"""Pollinations API provider (OpenAI-compatible)."""
import os
import requests
from dataclasses import dataclass

POLLINATIONS_URL = os.getenv("POLLINATIONS_URL", "https://gen.pollinations.ai/v1/chat/completions")
POLLINATIONS_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# Models sorted by speed (benchmark results)
POLLINATIONS_MODELS = [
    ("llama", "Meta Llama"),
    ("gemma", "Google Gemma"),
    ("deepseek", "DeepSeek"),
    ("openai", "OpenAI OSS"),
    ("mistral", "Mistral"),
    ("mistral-small-3.2", "Mistral Small"),
    ("grok", "Grok"),
    ("qwen-coder", "Qwen Coder"),
    ("nova-fast", "Nova Fast"),
    ("nova", "Nova"),
]


@dataclass
class _Msg:
    role: str = "assistant"
    content: str = None


@dataclass
class _Choice:
    message: _Msg = None
    finish_reason: str = "stop"
    index: int = 0


@dataclass
class _Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class _Response:
    id: str = ""
    model: str = ""
    choices: list = None
    usage: _Usage = None


class PollinationsClient:
    class _Completions:
        def __init__(self, parent):
            self._p = parent

        def create(self, model=None, messages=None, stream=False, **kwargs):
            model = model or self._p._model
            payload = {
                "model": model,
                "messages": messages or [],
                "stream": stream,
                "max_tokens": kwargs.get("max_tokens", 1024),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
            }
            headers = {"Content-Type": "application/json"}
            if self._p._api_key:
                headers["Authorization"] = f"Bearer {self._p._api_key}"
            resp = requests.post(
                POLLINATIONS_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            msg = data["choices"][0]["message"]
            return _Response(
                id=data.get("id", ""),
                model=data.get("model", model),
                choices=[_Choice(
                    message=_Msg(content=msg.get("content", "")),
                    finish_reason=data["choices"][0].get("finish_reason", "stop"),
                )],
                usage=_Usage(
                    prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                    completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
                    total_tokens=data.get("usage", {}).get("total_tokens", 0),
                ) if data.get("usage") else _Usage(),
            )

    class _Chat:
        def __init__(self, parent):
            self.completions = PollinationsClient._Completions(parent)

    def __init__(self, model="llama", api_key=None):
        self._model = model
        self._api_key = api_key or POLLINATIONS_KEY
        self.chat = PollinationsClient._Chat(self)
