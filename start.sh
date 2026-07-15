#!/bin/bash
set -e

PORT=${PORT:-10000}

# Generate prisma client if node is available
if command -v node &> /dev/null; then
    echo "Generating prisma client..."
    prisma generate || echo "prisma generate failed, continuing without DB"
fi

echo "Starting llm4free API on port 8000..."
uvicorn app:app --host 0.0.0.0 --port 8000 &
LLM4FREE_PID=$!

echo "Waiting for llm4free to be ready..."
sleep 3

echo "Starting LiteLLM proxy on port $PORT..."
litellm --port "$PORT" --config litellm_config.yaml &
LITELLM_PID=$!

echo "llm4free PID: $LLM4FREE_PID"
echo "LiteLLM PID: $LITELLM_PID"

wait $LLM4FREE_PID $LITELLM_PID
