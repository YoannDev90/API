from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/align", tags=["tools"])
async def text_align(body: TextInput, width: int = Query(default=80, ge=10, le=500),
                     alignment: str = Query(default="left")):
    words = body.text.split()
    lines = []; cur = ""
    for w in words:
        if len(cur)+len(w)+(1 if cur else 0) <= width: cur += (" " if cur else "") + w
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    if alignment == "right": lines = [l.rjust(width) for l in lines]
    elif alignment == "center": lines = [l.center(width) for l in lines]
    elif alignment == "justify":
        jl = []
        for l in lines:
            wl = l.split()
            if len(wl) <= 1: jl.append(l); continue
            spaces = width - sum(len(w) for w in wl)
            gaps = len(wl) - 1
            base, extra = divmod(spaces, gaps)
            r = ""
            for i, w in enumerate(wl):
                r += w
                if i < gaps: r += " " * (base + (1 if i < extra else 0))
            jl.append(r)
        lines = jl
    return {"code": "200", "alignment": alignment, "width": width, "lines": lines, "text": "\n".join(lines)}

