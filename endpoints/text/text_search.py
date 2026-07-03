from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/search", tags=["tools"])
async def text_search(body: TextInput, pattern: str = Query(..., description="Search pattern"),
                      context: int = Query(default=0, ge=0, le=10)):
    lines = body.text.splitlines()
    results = []
    for i, line in enumerate(lines):
        if pattern in line:
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            ctx = [{"line": j+1, "text": lines[j], "match": j==i} for j in range(start, end)]
            results.append({"line": i+1, "text": line, "context": ctx if context else None})
    return {"code": "200", "pattern": pattern, "matches": len(results), "results": results[:200]}

