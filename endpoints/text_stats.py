from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/text-stats", tags=["utils"])
async def text_stats(text: str = Query(..., description="Text to analyze")):
    words = text.split()
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    lines = text.count("\n") + 1
    return {
        "code": "200",
        "characters": chars, "characters_no_space": chars_no_space,
        "words": len(words), "lines": lines,
        "avg_word_length": round(sum(len(w) for w in words) / max(1, len(words)), 1),
    }

