# API Proxy

[![CI](https://img.shields.io/github/actions/workflow/status/YoannDev90/API/ci.yml?style=for-the-badge&logo=github&label=CI&branch=main)](https://github.com/YoannDev90/API/actions/workflows/ci.yml)
[![server](https://img.shields.io/badge/dynamic/json?style=for-the-badge&url=https%3A%2F%2Falphallm-api.onrender.com%2Fhealth&query=%24.status&label=server&cacheSeconds=300)](https://alphallm-api.onrender.com/health)
[![deploy](https://img.shields.io/badge/render-deployed?style=for-the-badge&logo=render&label=deploy)](https://dashboard.render.com/web/srv-d1j28ap5pdvs73cn2usg)

Proxy API with dynamic endpoint loading, rate limiting, and self-keepalive for Render.

## Structure

```
├── app.py
├── config.py
├── keep_alive.py
├── main.py
├── proxy.py
├── user_agents.json
├── .env.example
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── ENDPOINTS.md
├── scripts/
│   └── generate_docs.sh
├── tests/
│   ├── __init__.py
│   └── test_endpoints.py
├── .github/
│   └── workflows/ci.yml
└── endpoints/   (183 files, auto-discovered)
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
| `RENDER_EXTERNAL_URL` | no | Self-ping URL (Render only) |
| `PLAYWRIGHT_BROWSERS_PATH` | no | Playwright browsers path |
| `HOST` | no | Bind address (default `0.0.0.0`) |
| `PORT` | no | Port (default `8000`) |

## Keep-alive

Set `RENDER_EXTERNAL_URL` env var. Server pings `/health` every 10 min to prevent Render free tier sleep.

## Render deploy

Build command (with uv):

```
uv sync --no-dev && playwright install chromium --with-deps
```

Env vars: `PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.pw-browsers`
