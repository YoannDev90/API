#!/usr/bin/env python3
"""Benchmark LLM4Free providers - stream & non-stream, tok/s measurement."""
import time
import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

import tiktoken

sys.path.insert(0, str(Path(__file__).parent))

TEST_PROMPT = "Explain what a neural network is in exactly 2 sentences."

_enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens with tiktoken (cl100k_base)."""
    return len(_enc.encode(text))


def _get_provider(name):
    if name == "heckai":
        from llm4free import HeckAI
        return HeckAI(timeout=60)
    elif name == "freeai":
        from llm4free import FreeAI
        return FreeAI()
    elif name == "freeai_online":
        from llm4free import FreeAIOnline
        return FreeAIOnline()
    elif name == "deepai":
        from llm4free import DeepAI
        return DeepAI()
    elif name == "netwrck":
        from llm4free import Netwrck
        return Netwrck()
    elif name == "ai4chat":
        from llm4free import AI4Chat
        return AI4Chat()
    elif name == "wise_cat":
        from llm4free import WiseCat
        return WiseCat()
    elif name == "artingai":
        from llm4free import ArtingAI
        return ArtingAI()
    elif name == "chatgpt":
        from llm4free import ChatGPT
        return ChatGPT()
    elif name == "gptfree":
        from llm4free import GptFree
        return GptFree()
    return None


PROVIDERS = {
    "freeai":       {"models": ["qwen3-8b", "qwen7b"]},
    "deepai":       {"models": [
        "gpt-oss-120b", "gemini-2.5-flash-lite", "llama-4-scout",
        "llama-3.3-70b-instruct", "deepseek-v3.2", "llama-3.1-8b-instant",
        "gemini-3-pro", "gpt-4.1-nano", "qwen3-30b", "gpt-5-nano",
        "gemma-3-12b", "gemma2-9b", "standard", "super-genius",
    ]},
    "freeai_online": {"models": ["gpt-4o"]},
    "netwrck":       {"models": [
        "nvidia/llama-3.1-nemotron-70b-instruct", "deepseek/deepseek-chat",
        "minimax/minimax-m2.5",
    ]},
    "ai4chat":       {"models": [
        "codex-mini", "o1-pro", "o4-mini", "grok-4.1-fast",
        "gemini-3-flash", "gpt-4.1-nano", "gpt-3.5", "o3-mini-high",
        "o3-mini", "gpt-5.2", "gpt-4.5", "gpt-4o-mini-search-preview",
    ]},
    "heckai":        {"models": [
        "google/gemini-3.1-flash-lite", "google/gemini-3-flash-preview",
        "openai/gpt-5.4-mini", "minimax/minimax-m3",
        "deepseek/deepseek-v4-flash", "deepseek/deepseek-v4-pro",
        "stepfun/step-3.7-flash", "tencent/hy3-preview",
        "qwen/qwen3.7-plus",
    ]},
}


@dataclass
class ModelResult:
    provider: str
    model: str
    stream_ok: bool
    no_stream_ok: bool
    stream_latency_ms: float = 0
    no_stream_latency_ms: float = 0
    stream_tokens_per_sec: float = 0
    no_stream_tokens_per_sec: float = 0
    stream_tokens: int = 0
    no_stream_tokens: int = 0
    stream_content: str = ""
    no_stream_content: str = ""
    error_stream: str = ""
    error_no_stream: str = ""


def _extract_text(response):
    """Extract content from response object."""
    if hasattr(response, "choices") and response.choices:
        msg = getattr(response.choices[0], "message", None)
        if msg:
            return getattr(msg, "content", "") or ""
    return ""


def benchmark_model(provider_name: str, model: str, timeout: int = 30) -> ModelResult:
    """Benchmark one model: non-stream + stream. Returns ModelResult."""
    result = ModelResult(
        provider=provider_name,
        model=model,
        stream_ok=False,
        no_stream_ok=False,
    )

    messages = [{"role": "user", "content": TEST_PROMPT}]

    # --- NON-STREAM ---
    try:
        client = _get_provider(provider_name)
        if client:
            start = time.time()
            response = client.chat.completions.create(
                model=model, messages=messages, max_tokens=150, stream=False,
            )
            elapsed_ms = (time.time() - start) * 1000
            content = _extract_text(response).strip()
            tokens = count_tokens(content)
            toks_sec = (tokens / (elapsed_ms / 1000)) if elapsed_ms > 0 else 0
            result.no_stream_ok = bool(content)
            result.no_stream_latency_ms = round(elapsed_ms)
            result.no_stream_tokens = tokens
            result.no_stream_tokens_per_sec = round(toks_sec, 1)
            result.no_stream_content = content[:80]
    except Exception as e:
        result.error_no_stream = str(e)[:100]

    # --- STREAM ---
    try:
        client = _get_provider(provider_name)
        if client:
            start = time.time()
            stream = client.chat.completions.create(
                model=model, messages=messages, max_tokens=150, stream=True,
            )
            full_text = ""
            for chunk in stream:
                delta = getattr(chunk.choices[0], "delta", None) if chunk.choices else None
                if delta:
                    full_text += getattr(delta, "content", "") or ""
            elapsed_ms = (time.time() - start) * 1000
            content = full_text.strip()
            tokens = count_tokens(content)
            toks_sec = (tokens / (elapsed_ms / 1000)) if elapsed_ms > 0 else 0
            result.stream_ok = bool(content)
            result.stream_latency_ms = round(elapsed_ms)
            result.stream_tokens = tokens
            result.stream_tokens_per_sec = round(toks_sec, 1)
            result.stream_content = content[:80]
    except Exception as e:
        result.error_stream = str(e)[:100]

    return result


def main():
    print("=" * 100)
    print("  LLM4Free Benchmark v2 — non-stream + stream + tok/s")
    print("=" * 100)

    all_results: list[ModelResult] = []
    total_models = sum(len(p["models"]) for p in PROVIDERS.values())
    done = 0

    for provider_name, cfg in PROVIDERS.items():
        print(f"\n{'─' * 100}")
        print(f"  {provider_name.upper()}")
        print(f"{'─' * 100}")
        for model in cfg["models"]:
            done += 1
            print(f"  [{done}/{total_models}] {model:<50}", end="", flush=True)
            r = benchmark_model(provider_name, model)
            all_results.append(r)

            parts = []
            if r.no_stream_ok:
                parts.append(f"NS:✓ {r.no_stream_latency_ms}ms {r.no_stream_tokens_per_sec}tok/s")
            else:
                err = r.error_no_stream[:35] if r.error_no_stream else "empty"
                parts.append(f"NS:✗ {err}")
            if r.stream_ok:
                parts.append(f"S:✓ {r.stream_latency_ms}ms {r.stream_tokens_per_sec}tok/s")
            else:
                err = r.error_stream[:35] if r.error_stream else "empty"
                parts.append(f"S:✗ {err}")

            print(f"  │ {'  '.join(parts)}")

    # Summary
    working = [r for r in all_results if r.no_stream_ok or r.stream_ok]
    print(f"\n{'=' * 100}")
    print(f"  RESULTS — {len(working)}/{total_models} models working")
    print(f"{'=' * 100}")

    if working:
        print(f"\n{'Provider':<16} {'Model':<45} {'NS':<4} {'S':<4} {'NS tok/s':<10} {'S tok/s':<10} {'NS ms':<8} {'S ms':<8}")
        print("─" * 105)
        for r in sorted(working, key=lambda x: -(x.no_stream_tokens_per_sec + x.stream_tokens_per_sec)):
            ns = "✓" if r.no_stream_ok else "✗"
            st = "✓" if r.stream_ok else "✗"
            print(f"{r.provider:<16} {r.model:<45} {ns:<4} {st:<4} {r.no_stream_tokens_per_sec:<10} {r.stream_tokens_per_sec:<10} {r.no_stream_latency_ms:<8} {r.stream_latency_ms:<8}")

    # Save
    out = Path(__file__).parent / "benchmarks_results.json"
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M"),
        "test_prompt": TEST_PROMPT,
        "results": [asdict(r) for r in all_results],
        "summary": {
            "total": total_models,
            "working": len(working),
            "best_nosream": max(working, key=lambda x: x.no_stream_tokens_per_sec).model if working else None,
            "best_stream": max(working, key=lambda x: x.stream_tokens_per_sec).model if working else None,
        },
    }
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved → {out}")


if __name__ == "__main__":
    main()
