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
        for p in ["/", "/health", "/proxy", "/routes", "/uuid", "/whois", "/translate", "/screenshot", "/user-agents", "/hash", "/password", "/timestamp", "/dns", "/qr", "/markdown", "/color", "/text-stats", "/cron", "/jwt/decode", "/phone", "/country", "/regex/test", "/ssl", "/ports", "/http-status", "/password-strength", "/user-agent", "/json/format", "/random/number", "/roman", "/slugify", "/morse", "/dice", "/coin", "/date/diff", "/date/age", "/leap", "/bmi", "/convert", "/csp", "/week"]:
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


class TestUserAgents:
    def test_list(self):
        resp = client.get("/user-agents")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert len(data) > 5
        assert "Chrome 128 Windows" in data
        assert "Firefox 130 Linux" in data


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


class TestIPEnrichment:
    def test_ip_has_geo_field(self):
        resp = client.get("/ip")
        assert resp.status_code == 200
        assert "geo" in resp.json()

    def test_ip_geo_is_none_or_dict(self):
        resp = client.get("/ip")
        g = resp.json()["geo"]
        assert g is None or isinstance(g, dict)


class TestTranslate:
    def test_translate_missing_text(self):
        resp = client.post("/translate", json={})
        assert resp.status_code == 422

    def test_translate_invalid_lang(self):
        resp = client.post("/translate", json={"text": "hello", "target": "invalid"})
        assert resp.status_code == 502

    def test_translate_empty_text(self):
        resp = client.post("/translate", json={"text": ""})
        assert resp.status_code in (200, 422, 502)


class TestScreenshot:
    def test_screenshot_missing_url(self):
        resp = client.get("/screenshot")
        assert resp.status_code == 422

    def test_screenshot_invalid_url(self):
        resp = client.get("/screenshot?url=not-a-valid-url-xyz-123456")
        assert resp.status_code == 502


class TestHash:
    def test_hash(self):
        resp = client.post("/hash", json={"text": "hello"})
        assert resp.status_code == 200
        d = resp.json()
        assert d["md5"] == "5d41402abc4b2a76b9719d911017c592"
        assert len(d["sha256"]) == 64

    def test_hash_missing(self):
        assert client.post("/hash", json={}).status_code == 422


class TestPassword:
    def test_default_length(self):
        resp = client.get("/password")
        assert resp.status_code == 200
        assert len(resp.json()["password"]) == 20

    def test_custom_length(self):
        resp = client.get("/password?length=8")
        assert len(resp.json()["password"]) == 8

    def test_invalid_length(self):
        assert client.get("/password?length=200").status_code == 422
        assert client.get("/password?length=0").status_code == 422


class TestTimestamp:
    def test_valid(self):
        resp = client.get("/timestamp?value=1700000000")
        assert resp.status_code == 200
        d = resp.json()
        assert "2023" in d["iso_8601"]
        assert d["weekday"] in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

    def test_negative(self):
        resp = client.get("/timestamp?value=-1")
        assert resp.status_code in (200, 400)

    def test_missing(self):
        assert client.get("/timestamp").status_code == 422


class TestDNS:
    def test_a_record(self):
        resp = client.get("/dns?domain=example.com&type=A")
        assert resp.status_code == 200
        d = resp.json()
        assert d["type"] == "A"
        assert len(d["records"]) > 0

    def test_mx_record(self):
        resp = client.get("/dns?domain=example.com&type=MX")
        assert resp.status_code == 200
        assert len(resp.json()["records"]) > 0

    def test_invalid_type(self):
        assert client.get("/dns?domain=example.com&type=INVALID").status_code == 400

    def test_nxdomain(self):
        assert client.get("/dns?domain=nonexistent-domain-xyz123.com").status_code == 404

    def test_missing_domain(self):
        assert client.get("/dns?type=A").status_code == 422


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


class TestQR:
    def test_qr(self):
        resp = client.get("/qr?text=hello")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"

    def test_qr_missing(self):
        assert client.get("/qr").status_code == 422


class TestMarkdown:
    def test_markdown(self):
        resp = client.post("/markdown", json={"text": "# Hello\n**bold**"})
        assert resp.status_code == 200
        assert "<h1>" in resp.json()["html"]
        assert "<strong>" in resp.json()["html"]


class TestColor:
    def test_hex(self):
        resp = client.post("/color", json={"value": "#ff0000"})
        assert resp.status_code == 200
        d = resp.json()
        assert d["hex"] == "#ff0000"
        assert d["rgb"]["r"] == 255

    def test_rgb(self):
        resp = client.post("/color", json={"value": "rgb(0,255,0)"})
        assert resp.status_code == 200
        assert resp.json()["hex"] == "#00ff00"

    def test_invalid(self):
        assert client.post("/color", json={"value": "invalid"}).status_code == 400


class TestTextStats:
    def test_stats(self):
        resp = client.get("/text-stats?text=hello+world")
        assert resp.status_code == 200
        assert resp.json()["words"] == 2
        assert resp.json()["characters"] == 11


class TestCron:
    def test_cron(self):
        resp = client.get("/cron?expr=*/5+*+*+*+*")
        assert resp.status_code == 200
        assert len(resp.json()["next_5_runs"]) == 5

    def test_invalid(self):
        assert client.get("/cron?expr=invalid").status_code == 400


class TestJWT:
    def test_decode(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        resp = client.post("/jwt/decode", json={"token": token})
        assert resp.status_code == 200
        assert resp.json()["payload"]["sub"] == "1234567890"


class TestPhone:
    def test_phone(self):
        resp = client.get("/phone?number=%2B33612345678")
        assert resp.status_code == 200
        assert "France" in resp.json()["country"]

    def test_invalid(self):
        assert client.get("/phone?number=123").status_code == 400


class TestCountry:
    def test_fr(self):
        resp = client.get("/country?code=FR")
        assert resp.status_code == 200
        assert resp.json()["name"] == "France"

    def test_invalid(self):
        assert client.get("/country?code=ZZ").status_code == 404


class TestRegex:
    def test_match(self):
        resp = client.post("/regex/test", json={"pattern": "\\d+", "text": "abc123def456"})
        assert resp.status_code == 200
        assert resp.json()["match_count"] > 0

    def test_no_match(self):
        resp = client.post("/regex/test", json={"pattern": r"xyz", "text": "abcdef"})
        assert resp.status_code == 200
        assert not resp.json()["matched"]


class TestSSL:
    def test_ssl(self):
        resp = client.get("/ssl?domain=example.com")
        assert resp.status_code == 200
        assert "days_left" in resp.json()

    def test_invalid(self):
        assert client.get("/ssl?domain=invalid-domain-xyz-123.com").status_code == 502


class TestPorts:
    def test_scan(self):
        resp = client.get("/ports?host=example.com&ports=443")
        d = resp.json()
        assert "open_ports" in d
        assert d["total_scanned"] == 1


class TestHTTPStatus:
    def test_200(self):
        resp = client.get("/http-status?code=200")
        assert resp.json()["name"] == "OK"

    def test_404(self):
        resp = client.get("/http-status?code=404")
        assert resp.json()["name"] == "Not Found"

    def test_418(self):
        resp = client.get("/http-status?code=418")
        assert resp.json()["name"] == "I'm a Teapot"


class TestPasswordStrength:
    def test_weak(self):
        resp = client.get("/password-strength?password=123456")
        assert resp.status_code == 200
        assert "score" in resp.json()

    def test_strong(self):
        resp = client.get("/password-strength?password=f9kL%232mN%248xP%21qR7")
        assert resp.status_code == 200


class TestUserAgent:
    def test_chrome(self):
        resp = client.get("/user-agent?ua=" + "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36")
        assert resp.status_code == 200
        d = resp.json()
        assert "Chrome" in d["browser"]["family"]

    def test_bot(self):
        resp = client.get("/user-agent?ua=Googlebot/2.1")
        assert resp.json()["is_bot"]


class TestTools:
    def test_json_format(self):
        resp = client.post("/json/format", json={"data": '{"a":1,"b":2}'})
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/json"

    def test_random_number(self):
        resp = client.get("/random/number?min=1&max=10&count=5")
        assert resp.status_code == 200
        assert len(resp.json()["numbers"]) == 5

    def test_roman(self):
        resp = client.get("/roman?value=2024")
        assert resp.status_code == 200
        assert resp.json()["roman"] == "MMXXIV"

    def test_slugify(self):
        resp = client.get("/slugify?text=Hello+World!")
        assert resp.json()["slug"] == "hello-world"

    def test_morse(self):
        resp = client.get("/morse?text=SOS")
        assert resp.status_code == 200
        assert "..." in resp.json()["output"]

    def test_dice(self):
        resp = client.get("/dice?roll=2d6")
        assert resp.status_code == 200
        assert len(resp.json()["rolls"]) == 2

    def test_coin(self):
        resp = client.get("/coin?count=3")
        assert len(resp.json()["results"]) == 3

    def test_date_diff(self):
        resp = client.get("/date/diff?start=2024-01-01&end=2024-12-31")
        assert resp.json()["days"] == 365

    def test_leap(self):
        assert client.get("/leap?year=2024").json()["leap"] is True
        assert client.get("/leap?year=2023").json()["leap"] is False

    def test_bmi(self):
        resp = client.get("/bmi?weight=70&height=175")
        assert round(resp.json()["bmi"], 1) == 22.9

    def test_convert(self):
        resp = client.get("/convert?value=10&from=km&to=mi")
        assert abs(resp.json()["result"] - 6.2137) < 0.001

    def test_csp(self):
        resp = client.get("/csp")
        assert resp.status_code == 200
        assert "default-src" in resp.json()["csp"]

    def test_week(self):
        resp = client.get("/week?date=2024-01-01")
        assert resp.json()["week"] == 1


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
