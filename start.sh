#!/bin/bash
set -e

PORT=${PORT:-8000}
LITELLM_PORT=${LITELLM_PORT:-4000}

echo "Starting llm4free API on port $PORT..."
uvicorn app:app --host 0.0.0.0 --port "$PORT" &
LLM4FREE_PID=$!

echo "Waiting for llm4free to be ready..."
sleep 3

echo "Starting LiteLLM proxy on port $LITELLM_PORT..."
litellm --port "$LITELLM_PORT" --config litellm_config.yaml &
LITELLM_PID=$!

echo "llm4free PID: $LLM4FREE_PID"
echo "LiteLLM PID: $LITELLM_PID"

wait $LLM4FREE_PID $LITELLM_PID
