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
│   ├── 01_root.py
│   ├── 02_health.py
│   ├── 03_uptime.py
│   ├── 04_debug.py
│   ├── 05_favicon.py
│   ├── 06_proxy_custom.py
│   ├── 07_proxy_global.py
│   ├── 08_api_status.py
│   ├── 09_api_docs.py
│   ├── 10_api_resources.py
│   └── 99_api_catchall.py
└── requirements.txt
```

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

## Keep-alive

Set `RENDER_EXTERNAL_URL` env var. Server pings `/health` every 10 min to prevent Render free tier sleep.
