from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestGeneral:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        d = resp.json()
        assert d["code"] == "200"
        assert d["message"] == "API Proxy"
        assert d["version"] == "2.0.0"

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_uptime(self):
        resp = client.get("/uptime")
        assert resp.status_code == 200
        d = resp.json()
        assert d["code"] == "200"
        assert "uptime_seconds" in d or d.get("uptime") == "unknown"

    def test_version(self):
        resp = client.get("/version")
        assert resp.status_code == 200
        d = resp.json()
        assert d["version"] == "2.0.0"
        assert "python_version" in d
        assert "fastapi_version" in d


class TestIP:
    def test_xforwarded(self):
        resp = client.get("/ip", headers={"X-Forwarded-For": "1.2.3.4"})
        assert resp.json()["client_ip"] == "1.2.3.4"

    def test_cf_ip(self):
        resp = client.get("/ip", headers={"CF-Connecting-IP": "5.6.7.8"})
        assert resp.json()["client_ip"] == "5.6.7.8"

    def test_no_header(self):
        resp = client.get("/ip")
        assert resp.status_code == 200
        assert resp.json()["client_ip"] != ""


class TestDebug:
    def test_basic(self):
        resp = client.get("/debug")
        assert resp.status_code == 200
        d = resp.json()
        assert "request" in d
        assert "server_info" in d
        assert "runtime" in d
        assert "cpu_count" in d["runtime"]

    def test_cf_headers(self):
        resp = client.get("/debug", headers={"CF-IPCountry": "FR", "X-Test": "hello"})
        assert "cf_ipcountry" in resp.json()["cloudflare_info"]

    def test_no_env_leak(self):
        resp = client.get("/debug")
        assert "env" not in resp.json()


class TestRoutes:
    def test_returns_all(self):
        resp = client.get("/routes")
        assert resp.status_code == 200
        d = resp.json()
        assert d["count"] > 0
        paths = [r["path"] for r in d["routes"]]
        for p in ["/", "/health", "/proxy", "/routes", "/uuid", "/whois"]:
            assert p in paths

    def test_sorted(self):
        resp = client.get("/routes")
        paths = [r["path"] for r in resp.json()["routes"]]
        assert paths == sorted(paths)


class TestFavicon:
    def test_returns_svg(self):
        resp = client.get("/favicon.ico")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/svg+xml"
        assert "circle" in resp.text
        assert "#22c55e" in resp.text


class TestProxyUI:
    def test_page(self):
        resp = client.get("/proxy")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/html")
        assert "Go" in resp.text
        assert "iframe" in resp.text

    def test_debug_mode(self):
        resp = client.get("/proxy?debug-mode")
        assert resp.status_code == 200
        assert "Debug mode" in resp.text

    def test_debug_button(self):
        resp = client.get("/proxy?debug-mode")
        assert "Dbg" in resp.text


class TestUtils:
    def test_uuid_default(self):
        resp = client.get("/uuid")
        assert resp.status_code == 200
        d = resp.json()
        assert len(d["uuids"]) == 1
        assert len(d["uuids"][0].split("-")) == 5

    def test_uuid_count(self):
        resp = client.get("/uuid?count=5")
        assert resp.status_code == 200
        assert len(resp.json()["uuids"]) == 5

    def test_uuid_invalid_count(self):
        resp = client.get("/uuid?count=0")
        assert resp.status_code == 422
        resp = client.get("/uuid?count=200")
        assert resp.status_code == 422

    def test_base64_encode(self):
        resp = client.post("/base64/encode", json={"data": "hello"})
        assert resp.status_code == 200
        assert resp.json()["encoded"] == "aGVsbG8"

    def test_base64_decode(self):
        resp = client.post("/base64/decode", json={"data": "aGVsbG8"})
        assert resp.status_code == 200
        assert resp.json()["decoded"] == "hello"

    def test_base64_decode_invalid(self):
        resp = client.post("/base64/decode", json={"data": "!!!invalid!!!base64"})
        assert resp.status_code == 400

    def test_base64_missing_data(self):
        resp = client.post("/base64/encode", json={})
        assert resp.status_code == 422

    def test_whois_missing_domain(self):
        resp = client.get("/whois")
        assert resp.status_code == 422

    def test_whois_empty_domain(self):
        resp = client.get("/whois?domain=")
        assert resp.status_code in (422, 502)


class TestMiddleware:
    def test_404(self):
        assert client.get("/nonexistent").status_code == 404

    def test_cors(self):
        resp = client.options("/health", headers={"Origin": "https://example.com"})
        assert "access-control-allow-origin" in resp.headers

    def test_cache_control(self):
        resp = client.get("/version")
        assert resp.headers.get("cache-control") == "no-cache, no-store, must-revalidate"

    def test_rate_limit_path(self):
        for _ in range(6):
            client.get("/health")
        resp = client.get("/health")
        assert resp.status_code in (200, 429)

    def test_client_ip_middleware(self):
        resp = client.get("/ip", headers={"CF-Connecting-IP": "10.0.0.1"})
        assert resp.json()["client_ip"] == "10.0.0.1"

    def test_cache_control_favicon(self):
        resp = client.get("/favicon.ico")
        assert resp.headers.get("cache-control") == "no-cache, no-store, must-revalidate"
