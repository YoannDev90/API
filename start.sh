#!/bin/bash
set -e

PORT=${PORT:-10000}

echo "Starting llm4free API on internal port 8000..."
uvicorn app:app --host 127.0.0.1 --port 8000 &
LLM4FREE_PID=$!

echo "Waiting for llm4free to be ready..."
for i in $(seq 1 10); do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "llm4free is ready"
        break
    fi
    sleep 1
done

echo "Starting LiteLLM proxy on port $PORT..."
litellm --port "$PORT" --config litellm_config.yaml &
LITELLM_PID=$!

echo "llm4free PID: $LLM4FREE_PID"
echo "LiteLLM PID: $LITELLM_PID"

wait $LLM4FREE_PID $LITELLM_PID
