from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field
import io

class TextInput(BaseModel):
    text: str = Field(..., description="Input text")

@router.post("/text/table", tags=["tools"])
async def text_table(body: TextInput, delimiter: str = Query(default=",", description="Column delimiter"),
                     header: bool = Query(default=True)):
    rows = [r.split(delimiter) for r in body.text.splitlines() if r.strip()]
    if not rows: raise HTTPException(status_code=400, detail="No rows")
    cols = max(len(r) for r in rows)
    rows = [r + [""]*(cols-len(r)) for r in rows]
    w = [max(len(r[i]) for r in rows) for i in range(cols)]
    sep = "+" + "+".join("-"*(x+2) for x in w) + "+"
    from fastapi.responses import Response
    buf = io.StringIO()
    for idx, row in enumerate(rows):
        cells = " | ".join(c.ljust(x) for c,x in zip(row, w))
        buf.write(f"| {cells} |\n")
        if idx == 0 and header: buf.write(sep + "\n")
    return Response(content=sep + "\n" + buf.getvalue() + sep, media_type="text/plain; charset=utf-8")

