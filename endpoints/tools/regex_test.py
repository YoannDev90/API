from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import re

class RegexTestInput(BaseModel):
    pattern: str = Field(..., description="Regex pattern")
    text: str = Field(..., description="Text to test against")
    flags: str = Field(default="", description="Flags: i=ignore case, m=multiline, s=dotall")

@router.post("/regex/test", tags=["utils"])
async def regex_test(body: RegexTestInput):
    try:
        flags = 0
        if "i" in body.flags: flags |= re.IGNORECASE
        if "m" in body.flags: flags |= re.MULTILINE
        if "s" in body.flags: flags |= re.DOTALL
        compiled = re.compile(body.pattern, flags)
        matches = compiled.findall(body.text)
        return {"code": "200", "pattern": body.pattern, "match_count": len(matches), "matches": matches[:100], "matched": bool(matches)}
    except re.error as e:
        raise HTTPException(status_code=400, detail=f"Regex error: {e}")

