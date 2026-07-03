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
