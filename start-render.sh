#!/bin/bash
set -e

PORT=${PORT:-10000}

echo "Starting LiteLLM proxy on port $PORT..."
exec litellm --config litellm_config.yaml --port "$PORT" --host 0.0.0.0