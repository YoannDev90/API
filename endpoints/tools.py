import datetime
import json
import random
import re
import secrets
import string as str_mod
from logging import getLogger

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

router = APIRouter()
logger = getLogger("api-proxy")


class JSONInput(BaseModel):
    data: str = Field(..., description="JSON string")


@router.post("/json/format", tags=["tools"])
async def json_format(body: JSONInput):
    try:
        parsed = json.loads(body.data)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        return Response(content=formatted + "\n", media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")


@router.post("/json/minify", tags=["tools"])
async def json_minify(body: JSONInput):
    try:
        parsed = json.loads(body.data)
        return Response(content=json.dumps(parsed, separators=(",", ":"), ensure_ascii=False), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")


@router.get("/random/number", tags=["tools"])
async def random_number(min: int = Query(default=0), max: int = Query(default=100), count: int = Query(default=1, ge=1, le=100)):
    nums = [random.randint(min, max) for _ in range(count)]
    return {"code": "200", "min": min, "max": max, "count": count, "numbers": nums}


@router.get("/random/string", tags=["tools"])
async def random_string(length: int = Query(default=12, ge=1, le=256),
                        digits: bool = Query(default=True),
                        lowercase: bool = Query(default=True),
                        uppercase: bool = Query(default=True),
                        special: bool = Query(default=False)):
    chars = ""
    if digits: chars += str_mod.digits
    if lowercase: chars += str_mod.ascii_lowercase
    if uppercase: chars += str_mod.ascii_uppercase
    if special: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not chars: chars = str_mod.ascii_letters
    result = "".join(secrets.choice(chars) for _ in range(length))
    return {"code": "200", "length": length, "random_string": result}


class StringInput(BaseModel):
    text: str = Field(..., description="Input text")


@router.post("/string/reverse", tags=["tools"])
async def string_reverse(body: StringInput):
    return {"code": "200", "original": body.text, "reversed": body.text[::-1]}


@router.post("/string/count", tags=["tools"])
async def string_count(body: StringInput):
    from collections import Counter
    c = Counter(body.text)
    return {"code": "200", "length": len(body.text), "char_frequency": dict(c.most_common(50))}


@router.post("/string/repeat", tags=["tools"])
async def string_repeat(body: StringInput, times: int = Query(default=2, ge=1, le=1000)):
    return {"code": "200", "original": body.text, "repeated": body.text * times, "times": times}


@router.get("/math", tags=["tools"])
async def math_eval(expr: str = Query(..., description="Math expression (e.g. 2+2*3)")):
    allowed = re.compile(r"^[\d\s+\-*/().,%^]+$")
    if not allowed.match(expr):
        raise HTTPException(status_code=400, detail="Expression contains invalid characters")
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        return {"code": "200", "expression": expr, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Math error: {e}")


@router.get("/roman", tags=["tools"])
async def roman_numeral(value: str = Query(..., description="Number (e.g. 2024) or Roman numeral (e.g. MMXXIV)"),
                        direction: str = Query(default="to_roman", description="to_roman or to_number")):
    if direction == "to_roman":
        try:
            n = int(value)
            if n < 1 or n > 3999:
                raise HTTPException(status_code=400, detail="Number must be 1-3999")
            vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                    (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
            result = ""
            for v, r in vals:
                while n >= v:
                    result += r
                    n -= v
            return {"code": "200", "number": value, "roman": result}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid number")
    else:
        roman = value.upper()
        vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
        try:
            result = 0
            for i in range(len(roman)):
                if i + 1 < len(roman) and vals[roman[i]] < vals[roman[i + 1]]:
                    result -= vals[roman[i]]
                else:
                    result += vals[roman[i]]
            return {"code": "200", "roman": value, "number": result}
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Roman numeral")


@router.get("/slugify", tags=["tools"])
async def slugify(text: str = Query(..., description="Text to slugify"), separator: str = Query(default="-")):
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", separator, slug)
    slug = slug.strip(separator)
    return {"code": "200", "original": text, "slug": slug}


@router.get("/morse", tags=["tools"])
async def morse_code(text: str = Query(..., description="Text to convert"),
                     direction: str = Query(default="encode", description="encode or decode")):
    morse_map = {
        "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
        "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.",
        "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
        "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
        "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.", ".": ".-.-.-", ",": "--..--",
        "?": "..--..", "'": ".----.", "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-",
        "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-", "+": ".-.-.", "-": "-....-",
        "_": "..--.-", "\"": ".-..-.", "@": ".--.-.", " ": "/",
    }
    rev_map = {v: k for k, v in morse_map.items()}
    try:
        if direction == "encode":
            result = " ".join(morse_map.get(c.upper(), c) for c in text)
        else:
            words = text.split(" / ")
            result = "".join("".join(rev_map.get(c, c) for c in w.split()) for w in words)
        return {"code": "200", "direction": direction, "input": text, "output": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Morse error: {e}")


@router.get("/dice", tags=["tools"])
async def dice_roller(roll: str = Query(default="1d6", description="Dice notation (e.g. 2d6, 3d20, 1d10+5)")):
    try:
        m = re.match(r"^(\d+)d(\d+)(?:\+(\d+))?$", roll.lower())
        if not m:
            raise HTTPException(status_code=400, detail="Invalid dice notation. Use format: NdS or NdS+M (e.g. 2d6, 3d20+5)")
        count, sides, bonus = int(m.group(1)), int(m.group(2)), int(m.group(3)) if m.group(3) else 0
        if count < 1 or count > 100 or sides < 2 or sides > 1000:
            raise HTTPException(status_code=400, detail="Count must be 1-100, sides 2-1000")
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + bonus
        return {
            "code": "200",
            "notation": roll,
            "rolls": rolls,
            "subtotal": sum(rolls),
            "bonus": bonus,
            "total": total,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dice error: {e}")


@router.get("/coin", tags=["tools"])
async def coin_flip(count: int = Query(default=1, ge=1, le=100)):
    results = [secrets.choice(["heads", "tails"]) for _ in range(count)]
    return {"code": "200", "count": count, "results": results, "heads": results.count("heads"), "tails": results.count("tails")}


@router.get("/date/diff", tags=["tools"])
async def date_diff(start: str = Query(..., description="Start date (YYYY-MM-DD)"),
                    end: str = Query(..., description="End date (YYYY-MM-DD)")):
    try:
        s = datetime.date.fromisoformat(start)
        e = datetime.date.fromisoformat(end)
        delta = (e - s).days
        return {
            "code": "200",
            "start": start, "end": end,
            "days": abs(delta),
            "weeks": round(abs(delta) / 7, 1),
            "months": round(abs(delta) / 30.44, 1),
            "years": round(abs(delta) / 365.25, 1),
            "direction": "forward" if delta >= 0 else "backward",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Date error: {e}")


@router.get("/date/age", tags=["tools"])
async def age_calculator(birth: str = Query(..., description="Birth date (YYYY-MM-DD)")):
    try:
        b = datetime.date.fromisoformat(birth)
        today = datetime.date.today()
        age = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
        next_birthday = datetime.date(today.year, b.month, b.day)
        if next_birthday < today:
            next_birthday = datetime.date(today.year + 1, b.month, b.day)
        days_to_next = (next_birthday - today).days
        return {"code": "200", "birth": birth, "age": age, "next_birthday": str(next_birthday), "days_to_next_birthday": days_to_next}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Age error: {e}")


@router.get("/leap", tags=["tools"])
async def leap_year(year: int = Query(..., description="Year (e.g. 2024)", ge=1, le=9999)):
    leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    return {"code": "200", "year": year, "leap": leap, "days": 366 if leap else 365}


@router.get("/bmi", tags=["tools"])
async def bmi_calculator(weight: float = Query(..., description="Weight in kg", gt=0),
                         height: float = Query(..., description="Height in cm", gt=0)):
    bmi = round(weight / ((height / 100) ** 2), 2)
    if bmi < 18.5: category = "underweight"
    elif bmi < 25: category = "healthy"
    elif bmi < 30: category = "overweight"
    else: category = "obese"
    return {"code": "200", "weight_kg": weight, "height_cm": height, "bmi": bmi, "category": category}


@router.get("/percentage", tags=["tools"])
async def percentage_calc(value: float = Query(..., description="Part value"),
                          total: float = Query(..., description="Total value", gt=0)):
    pct = round(value / total * 100, 2)
    return {"code": "200", "value": value, "total": total, "percentage": pct, "label": f"{value} is {pct}% of {total}"}


UNITS = {
    "length": {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.34, "yd": 0.9144, "ft": 0.3048, "in": 0.0254},
    "weight": {"kg": 1, "g": 0.001, "mg": 1e-6, "lb": 0.453592, "oz": 0.0283495},
    "volume": {"l": 1, "ml": 0.001, "gal": 3.78541, "qt": 0.946353, "pt": 0.473176, "cup": 0.236588, "fl_oz": 0.0295735},
}


@router.get("/convert", tags=["tools"])
async def unit_convert(value: float = Query(..., description="Value to convert"),
                       from_: str = Query(alias="from", description="Source unit (e.g. km, kg, l)"),
                       to: str = Query(..., description="Target unit (e.g. mi, lb, gal)")):
    for category, units in UNITS.items():
        if from_ in units and to in units:
            result = round(value * units[from_] / units[to], 6)
            return {"code": "200", "category": category, "value": value, "from": from_, "to": to, "result": result}
    raise HTTPException(status_code=400, detail=f"Unknown units. Supported: length (km/m/cm/mm/mi/yd/ft/in), weight (kg/g/mg/lb/oz), volume (l/ml/gal/qt/pt/cup/fl_oz)")


@router.get("/csp", tags=["tools"])
async def csp_generator(
    default_src: str = Query(default="'self'"),
    script_src: str = Query(default="'self'"),
    style_src: str = Query(default="'self'"),
    img_src: str = Query(default="'self' data:"),
    connect_src: str = Query(default="'self'"),
    font_src: str = Query(default="'self'"),
    frame_src: str = Query(default=""),
    report_uri: str = Query(default=""),
):
    directives = []
    for name, val in [("default-src", default_src), ("script-src", script_src), ("style-src", style_src),
                       ("img-src", img_src), ("connect-src", connect_src), ("font-src", font_src),
                       ("frame-src", frame_src)]:
        if val:
            directives.append(f"{name} {val}")
    if report_uri:
        directives.append(f"report-uri {report_uri}")
    csp = "; ".join(directives)
    return {"code": "200", "csp": csp, "header": f"Content-Security-Policy: {csp}"}


@router.get("/week", tags=["tools"])
async def week_number(date: str = Query(default=None, description="Date (YYYY-MM-DD), defaults to today")):
    d = datetime.date.fromisoformat(date) if date else datetime.date.today()
    iso = d.isocalendar()
    return {"code": "200", "date": str(d), "week": iso[1], "year": iso[0], "weekday": d.strftime("%A"), "day_of_year": d.timetuple().tm_yday}


# ── HTTP tools ──────────────────────────────────────────────────────────────


@router.get("/headers", tags=["tools"])
async def fetch_headers(url: str = Query(..., description="URL to fetch")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=False) as c:
            resp = await c.get(url)
        return {"code": "200", "url": url, "status": resp.status_code, "headers": dict(resp.headers)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/redirects", tags=["tools"])
async def trace_redirects(url: str = Query(..., description="URL to trace")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        chain = []
        async with httpx.AsyncClient(timeout=10, follow_redirects=False) as c:
            for _ in range(20):
                resp = await c.get(url)
                chain.append({"url": url, "status": resp.status_code, "headers": dict(resp.headers)})
                if resp.status_code in (301, 302, 303, 307, 308):
                    url = resp.headers.get("location", "")
                    if not url:
                        break
                else:
                    break
        return {"code": "200", "chain": chain, "hops": len(chain)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/cookies", tags=["tools"])
async def fetch_cookies(url: str = Query(..., description="URL to fetch")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            resp = await c.get(url)
        cookies = [{"name": k, "value": v} for k, v in c.cookies.items()] if hasattr(c, "cookies") else []
        return {"code": "200", "url": url, "status": resp.status_code, "cookies": cookies}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/robots", tags=["tools"])
async def fetch_robots(url: str = Query(..., description="Site URL (e.g. example.com)")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    robots_url = url.rstrip("/") + "/robots.txt"
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(robots_url)
        if resp.status_code != 200:
            return {"code": "200", "url": robots_url, "status": resp.status_code, "content": None}
        text = resp.text
        disallow = [l.split(":", 1)[1].strip() for l in text.splitlines() if l.lower().startswith("disallow")]
        allow = [l.split(":", 1)[1].strip() for l in text.splitlines() if l.lower().startswith("allow")]
        sitemaps = [l.split(":", 1)[1].strip() for l in text.splitlines() if l.lower().startswith("sitemap")]
        return {"code": "200", "url": robots_url, "disallow": disallow, "allow": allow, "sitemaps": sitemaps, "raw": text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/sitemap", tags=["tools"])
async def fetch_sitemap(url: str = Query(..., description="Sitemap URL (e.g. example.com/sitemap.xml)")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            resp = await c.get(url)
        if resp.status_code != 200:
            return {"code": "200", "url": url, "status": resp.status_code, "urls": None}
        import re
        urls = re.findall(r"<loc>(.*?)</loc>", resp.text)
        return {"code": "200", "url": url, "count": len(urls), "urls": urls[:500]}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Math & Stats ────────────────────────────────────────────────────────────


@router.get("/stats", tags=["tools"])
async def statistics(values: str = Query(..., description="Comma-separated numbers (e.g. 1,2,3,4,5)")):
    try:
        nums = [float(x.strip()) for x in values.split(",")]
        n = len(nums)
        s = sum(nums)
        mean = s / n
        sorted_nums = sorted(nums)
        median = sorted_nums[n // 2] if n % 2 else (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2
        from collections import Counter
        c = Counter(nums)
        mode = [k for k, v in c.items() if v == max(c.values())]
        variance = sum((x - mean) ** 2 for x in nums) / (n - 1) if n > 1 else 0
        stddev = variance ** 0.5
        rng = max(nums) - min(nums)
        q1 = sorted_nums[n // 4] if n % 4 else (sorted_nums[n // 4 - 1] + sorted_nums[n // 4]) / 2
        q3 = sorted_nums[3 * n // 4] if (3 * n) % 4 else (sorted_nums[3 * n // 4 - 1] + sorted_nums[3 * n // 4]) / 2
        return {
            "code": "200",
            "count": n, "sum": s, "min": min(nums), "max": max(nums), "range": rng,
            "mean": round(mean, 4), "median": round(median, 4), "mode": mode,
            "q1": round(q1, 4), "q3": round(q3, 4),
            "variance": round(variance, 4), "stddev": round(stddev, 4),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prime", tags=["tools"])
async def primes_up_to(n: int = Query(default=100, ge=2, le=100000, description="Upper limit")):
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i : n + 1 : i] = b"\x00" * (((n - i * i) // i) + 1)
    primes = [i for i, v in enumerate(sieve) if v]
    return {"code": "200", "limit": n, "count": len(primes), "primes": primes[:500]}


@router.get("/fibonacci", tags=["tools"])
async def fibonacci(n: int = Query(default=10, ge=1, le=1000, description="Number of terms")):
    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return {"code": "200", "terms": n, "sequence": seq[:n]}


@router.get("/factorial", tags=["tools"])
async def factorial(n: int = Query(..., description="Number", ge=0, le=500)):
    import math
    return {"code": "200", "n": n, "factorial": math.factorial(n)}


@router.get("/gcd", tags=["tools"])
async def gcd_lcm(a: int = Query(..., description="First number", ge=1), b: int = Query(..., description="Second number", ge=1)):
    import math
    return {"code": "200", "a": a, "b": b, "gcd": math.gcd(a, b), "lcm": a * b // math.gcd(a, b)}


# ── Text tools ──────────────────────────────────────────────────────────────


class TextInput(BaseModel):
    text: str = Field(..., description="Input text")


@router.post("/text/search", tags=["tools"])
async def text_search(body: TextInput, pattern: str = Query(..., description="Search pattern"), context: int = Query(default=0, ge=0, le=10)):
    lines = body.text.splitlines()
    results = []
    for i, line in enumerate(lines):
        if pattern in line:
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            ctx = [{"line": j + 1, "text": lines[j], "match": j == i} for j in range(start, end)]
            results.append({"line": i + 1, "text": line, "context": ctx if context else None})
    return {"code": "200", "pattern": pattern, "matches": len(results), "results": results[:200]}


@router.post("/text/sort", tags=["tools"])
async def text_sort(body: TextInput, reverse: bool = Query(default=False), numeric: bool = Query(default=False)):
    lines = body.text.splitlines(keepends=True)
    if numeric:
        lines.sort(key=lambda x: float(x.strip()), reverse=reverse)
    else:
        lines.sort(reverse=reverse)
    return {"code": "200", "sorted": "".join(lines), "lines": len(lines)}


@router.post("/text/dedup", tags=["tools"])
async def text_dedup(body: TextInput):
    seen = set()
    result = []
    for line in body.text.splitlines():
        if line not in seen:
            seen.add(line)
            result.append(line)
    return {"code": "200", "deduped": "\n".join(result), "original_lines": len(body.text.splitlines()), "unique_lines": len(result)}


@router.post("/text/columns", tags=["tools"])
async def text_columns(body: TextInput, col: int = Query(default=1, ge=1, description="Column number (1-indexed)"),
                       delimiter: str = Query(default=" ", description="Column delimiter")):
    lines = body.text.splitlines()
    extracted = []
    for i, line in enumerate(lines):
        parts = line.split(delimiter)
        if col <= len(parts):
            extracted.append(parts[col - 1])
    return {"code": "200", "column": col, "delimiter": delimiter, "values": extracted, "count": len(extracted)}


@router.post("/text/table", tags=["tools"])
async def text_table(body: TextInput, delimiter: str = Query(default=",", description="Column delimiter"),
                     header: bool = Query(default=True, description="First row is header")):
    import io
    rows = [row.split(delimiter) for row in body.text.splitlines() if row.strip()]
    if not rows:
        raise HTTPException(status_code=400, detail="No rows")
    cols = max(len(r) for r in rows)
    rows = [r + [""] * (cols - len(r)) for r in rows]
    widths = [max(len(r[i]) for r in rows) for i in range(cols)]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    buf = io.StringIO()
    for idx, row in enumerate(rows):
        cells = " | ".join(cell.ljust(w) for cell, w in zip(row, widths))
        buf.write(f"| {cells} |\n")
        if idx == 0 and header:
            buf.write(sep + "\n")
    table = sep + "\n" + buf.getvalue() + sep
    return Response(content=table, media_type="text/plain; charset=utf-8")


@router.post("/text/align", tags=["tools"])
async def text_align(body: TextInput, width: int = Query(default=80, ge=10, le=500), alignment: str = Query(default="left")):
    words = body.text.split()
    lines = []
    current = ""
    for w in words:
        if len(current) + len(w) + (1 if current else 0) <= width:
            current += (" " if current else "") + w
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    if alignment == "right":
        lines = [l.rjust(width) for l in lines]
    elif alignment == "center":
        lines = [l.center(width) for l in lines]
    elif alignment == "justify":
        justified = []
        for l in lines:
            words_l = l.split()
            if len(words_l) == 1:
                justified.append(l)
            else:
                spaces = width - sum(len(w) for w in words_l)
                gaps = len(words_l) - 1
                extra = spaces % gaps
                base = spaces // gaps
                result = ""
                for i, w in enumerate(words_l):
                    result += w
                    if i < gaps:
                        result += " " * (base + (1 if i < extra else 0))
                justified.append(result)
        lines = justified
    return {"code": "200", "alignment": alignment, "width": width, "lines": lines, "text": "\n".join(lines)}


# ── Network tools ───────────────────────────────────────────────────────────


@router.get("/rdap", tags=["tools"])
async def rdap_lookup(ip: str = Query(..., description="IP address")):
    import ipaddress
    try:
        ipaddress.ip_address(ip)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid IP address")
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(f"https://rdap.db.ripe.net/ip/{ip}")
        if resp.status_code == 200:
            d = resp.json()
            return {
                "code": "200",
                "ip": ip,
                "handle": d.get("handle"),
                "name": d.get("name"),
                "type": d.get("type"),
                "country": d.get("country"),
                "start_address": d.get("startAddress"),
                "end_address": d.get("endAddress"),
                "entities": [e.get("vcardArray", [[""]])[1][0][3] if e.get("vcardArray") else e.get("handle") for e in d.get("entities", [])[:5]],
            }
        return {"code": "200", "ip": ip, "rdap": resp.json() if resp.status_code < 500 else None}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/asn", tags=["tools"])
async def asn_lookup(ip: str = Query(..., description="IP address")):
    import ipaddress
    try:
        ipaddress.ip_address(ip)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid IP address")
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            resp = await c.get(f"https://rdap.db.ripe.net/ip/{ip}")
        if resp.status_code == 200:
            d = resp.json()
            entities = d.get("entities", [])
            asn_data = None
            for autnum in d.get("links", []):
                if "autnum" in autnum.get("href", ""):
                    ar = await c.get(autnum["href"])
                    if ar.status_code == 200:
                        ad = ar.json()
                        asn_data = {"asn": ad.get("handle"), "name": ad.get("name"), "country": ad.get("country")}
                        break
            if not asn_data:
                for e in entities:
                    for link in e.get("links", []):
                        if "autnum" in link.get("href", ""):
                            ar = await c.get(link["href"])
                            if ar.status_code == 200:
                                ad = ar.json()
                                asn_data = {"asn": ad.get("handle"), "name": ad.get("name"), "country": ad.get("country")}
                                break
                    if asn_data:
                        break
            return {"code": "200", "ip": ip, "asn": asn_data}
        return {"code": "200", "ip": ip, "asn": None}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Color tools ─────────────────────────────────────────────────────────────


@router.get("/color/random", tags=["tools"])
async def random_color():
    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    hex_c = f"#{r:02x}{g:02x}{b:02x}"
    return {"code": "200", "hex": hex_c, "rgb": {"r": r, "g": g, "b": b}}


@router.get("/color/palette", tags=["tools"])
async def color_palette(base: str = Query(default=None, description="Base hex color (e.g. #ff0000)"), count: int = Query(default=5, ge=2, le=20)):
    if base:
        base = base.lstrip("#")
        r, g, b = int(base[0:2], 16), int(base[2:4], 16), int(base[4:6], 16)
        base_rgb = (r, g, b)
    else:
        base_rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    palette = []
    for i in range(count):
        t = i / (count - 1) if count > 1 else 0.5
        shift = t * 60 - 30
        nr = max(0, min(255, int(base_rgb[0] + shift)))
        ng = max(0, min(255, int(base_rgb[1] - shift * 0.5)))
        nb = max(0, min(255, int(base_rgb[2] + shift * 1.5)))
        palette.append(f"#{nr:02x}{ng:02x}{nb:02x}")
    return {"code": "200", "base": f"#{base_rgb[0]:02x}{base_rgb[1]:02x}{base_rgb[2]:02x}", "palette": palette}


@router.get("/unicode", tags=["tools"])
async def unicode_info(char: str = Query(..., description="Character (e.g. A, €, 🔥)")):
    if len(char) != 1:
        raise HTTPException(status_code=400, detail="Enter exactly one character")
    cp = ord(char)
    name = None
    try:
        import unicodedata
        name = unicodedata.name(char)
    except ValueError:
        name = "Unknown"
    category = unicodedata.category(char)
    return {
        "code": "200",
        "char": char,
        "codepoint": f"U+{cp:04X}",
        "decimal": cp,
        "hex": hex(cp),
        "binary": bin(cp),
        "name": name,
        "category": category,
        "category_name": {
            "Lu": "Letter uppercase", "Ll": "Letter lowercase", "Lt": "Letter titlecase",
            "Lm": "Letter modifier", "Lo": "Letter other",
            "Mn": "Mark nonspacing", "Mc": "Mark spacing", "Me": "Mark enclosing",
            "Nd": "Number decimal", "Nl": "Number letter", "No": "Number other",
            "Pc": "Punctuation connector", "Pd": "Punctuation dash", "Ps": "Punctuation open",
            "Pe": "Punctuation close", "Pi": "Punctuation initial", "Pf": "Punctuation final",
            "Po": "Punctuation other",
            "Sm": "Symbol math", "Sc": "Symbol currency", "Sk": "Symbol modifier",
            "So": "Symbol other",
            "Zs": "Separator space", "Zl": "Separator line", "Zp": "Separator paragraph",
            "Cc": "Control", "Cf": "Format", "Cs": "Surrogate", "Co": "Private use",
        }.get(category, "Other"),
    }


# ── Misc tools ──────────────────────────────────────────────────────────────


class SplitInput(BaseModel):
    text: str = Field(..., description="Text to split")
    delimiter: str = Field(default=",", description="Delimiter")


@router.post("/split", tags=["tools"])
async def split_text(body: SplitInput):
    parts = body.text.split(body.delimiter)
    return {"code": "200", "delimiter": body.delimiter, "count": len(parts), "parts": parts}


@router.post("/join", tags=["tools"])
async def join_text(body: SplitInput):
    result = body.delimiter.join(body.text.splitlines())
    return {"code": "200", "delimiter": body.delimiter, "result": result}
