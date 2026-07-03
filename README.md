# API Proxy

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
│   └── api_catchall.py      # /api/{path:path} (catch-all, loaded last)
└── requirements.txt
```

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

## Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Keep-alive

Set `RENDER_EXTERNAL_URL` env var. Server pings `/health` every 10 min to prevent Render free tier sleep.
