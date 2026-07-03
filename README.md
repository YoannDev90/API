# API Proxy

[![CI](https://img.shields.io/github/actions/workflow/status/YoannDev90/API/ci.yml?style=for-the-badge&logo=github&label=CI&branch=main)](https://github.com/YoannDev90/API/actions/workflows/ci.yml)
[![server](https://img.shields.io/badge/dynamic/json?style=for-the-badge&url=https%3A%2F%2Falphallm-api.onrender.com%2Fhealth&query=%24.status&label=server&cacheSeconds=300)](https://alphallm-api.onrender.com/health)
[![deploy](https://img.shields.io/badge/render-deployed?style=for-the-badge&logo=render&label=deploy)](https://dashboard.render.com/web/srv-d1j28ap5pdvs73cn2usg)

Proxy API with dynamic endpoint loading, rate limiting, and self-keepalive for Render.

## Structure

```
├── app.py              # FastAPI app, middleware, dynamic endpoint loader
├── main.py             # Entry point (uvicorn)
├── config.py           # Configuration from env vars
├── proxy.py            # Proxy logic (internal + general)
├── keep_alive.py       # Self-ping to prevent Render sleep
├── endpoints/          # One file per endpoint, loaded dynamically
│   ├── root.py              # GET /
│   ├── health.py            # GET /health
│   ├── uptime.py            # GET /uptime
│   ├── version.py           # GET /version
│   ├── client_ip.py         # GET /ip
│   ├── debug.py             # GET /debug
│   ├── favicon.py           # GET /favicon.ico
│   ├── list_routes.py       # GET /routes
│   ├── proxy_global.py      # GET /proxy (UI) + /proxy/{path:path} (proxy)
│   └── utils.py             # GET /whois, /uuid, POST /base64/*
└── requirements.txt
```

## Quick start

```bash
# copy env file
cp .env.example .env
# edit .env with your DATA_SERVICE_BASE_URL

# with pip
pip install -r requirements.txt
python main.py

# or with uv
uv sync
uv run python main.py
```

## Tests

```bash
# pip
pip install pytest
python -m pytest tests/ -v

# uv
uv sync --dev
uv run pytest tests/ -v
```

## Env vars

| Var | Required | Description |
|-----|----------|-------------|
| `DATA_SERVICE_BASE_URL` | yes | Upstream API base URL |
| `RENDER_EXTERNAL_URL` | no | Self-ping URL (Render only) |
| `HOST` | no | Bind address (default `0.0.0.0`) |
| `PORT` | no | Port (default `8000`) |

## Keep-alive

Set `RENDER_EXTERNAL_URL` env var. Server pings `/health` every 10 min to prevent Render free tier sleep.

## Render deploy

Build command (with uv):

```
uv sync --no-dev
```
