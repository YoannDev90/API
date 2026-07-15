#!/bin/bash
set -e

PORT=${PORT:-8000}

echo "Starting LLM API on port $PORT..."
exec uvicorn app:app --host 0.0.0.0 --port "$PORT"