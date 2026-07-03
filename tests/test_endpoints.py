from fastapi.testclient import TestClient
from app import app
from config import allowed_proxy_paths

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert data["message"] == "API Proxy"
    assert data["version"] == "2.0.0"


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert data["status"] == "healthy"


def test_ping():
    resp = client.get("/ping")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert data["message"] == "pong"


def test_uptime():
    resp = client.get("/uptime")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert "uptime_seconds" in data or data.get("uptime") == "unknown"


def test_version():
    resp = client.get("/version")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert data["version"] == "2.0.0"
    assert "python_version" in data
    assert "fastapi_version" in data


def test_client_ip():
    resp = client.get("/ip", headers={"X-Forwarded-For": "1.2.3.4"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert data["client_ip"] == "1.2.3.4"


def test_client_ip_cf():
    resp = client.get("/ip", headers={"CF-Connecting-IP": "5.6.7.8"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["client_ip"] == "5.6.7.8"


def test_debug():
    resp = client.get("/debug")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert "request" in data
    assert "server_info" in data
    assert "runtime" in data
    assert "cpu_count" in data["runtime"]


def test_debug_with_headers():
    resp = client.get("/debug", headers={"CF-IPCountry": "FR", "X-Test": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert "cf_ipcountry" in data["cloudflare_info"]


def test_routes():
    resp = client.get("/routes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == "200"
    assert data["count"] > 0
    paths = [r["path"] for r in data["routes"]]
    assert "/" in paths
    assert "/health" in paths
    assert "/debug" in paths
    assert "/routes" in paths
    assert "/favicon.ico" in paths


def test_favicon():
    resp = client.get("/favicon.ico")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/svg+xml"
    assert "circle" in resp.text
    assert "#22c55e" in resp.text


def test_404():
    resp = client.get("/nonexistent")
    assert resp.status_code == 404


def test_rate_limiting():
    for _ in range(6):
        client.get("/ping")
    resp = client.get("/ping")
    assert resp.status_code in (200, 429)


def test_cors_headers():
    resp = client.options("/ping", headers={"Origin": "https://example.com"})
    assert "access-control-allow-origin" in resp.headers


def test_cache_control():
    resp = client.get("/version")
    assert resp.status_code == 200
    assert resp.headers.get("cache-control") == "no-cache, no-store, must-revalidate"
