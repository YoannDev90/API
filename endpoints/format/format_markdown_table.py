from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


import csv, io
from pydantic import BaseModel, Field

class CSVInput(BaseModel):
    data: str = Field(..., description="CSV data")
    header: bool = Field(default=True, description="First row is header")

@router.post("/format/markdown-table", tags=["format"])
async def format_markdown(body: CSVInput):
    reader = csv.reader(io.StringIO(body.data))
    rows = list(reader)
    if not rows: raise HTTPException(status_code=400, detail="No rows")
    cols = len(rows[0])
    col_widths = [max(len(r[i]) for r in rows) for i in range(cols)]
    lines = []
    for idx, row in enumerate(rows):
        line = "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
        lines.append(line)
        if idx == 0 and body.header:
            sep = "| " + " | ".join("-" * w for w in col_widths) + " |"
            lines.append(sep)
    return {"code": "200", "table": "\n".join(lines)}
