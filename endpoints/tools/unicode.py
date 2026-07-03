from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/unicode", tags=["tools"])
async def unicode_info(char: str = Query(..., description="Character")):
    if len(char) != 1: raise HTTPException(status_code=400, detail="Enter exactly one character")
    import unicodedata
    cp = ord(char)
    try: name = unicodedata.name(char)
    except ValueError: name = "Unknown"
    return {"code": "200", "char": char, "codepoint": f"U+{cp:04X}", "decimal": cp, "hex": hex(cp), "binary": bin(cp),
            "name": name, "category": unicodedata.category(char)}

