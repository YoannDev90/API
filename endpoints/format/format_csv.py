from logging import getLogger
from fastapi import APIRouter, HTTPException


logger = getLogger("api-proxy")
router = APIRouter()


import csv, io
from pydantic import BaseModel, Field

class TableInput(BaseModel):
    text: str = Field(..., description="Space/tab-delimited text")
    delimiter: str = Field(default=" ", description="Input delimiter")

@router.post("/format/csv", tags=["format"])
async def format_csv(body: TableInput):
    rows = [line.split(body.delimiter) for line in body.text.splitlines() if line.strip()]
    if not rows: raise HTTPException(status_code=400, detail="No data")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerows(rows)
    from fastapi.responses import Response
    return Response(content=buf.getvalue(), media_type="text/csv; charset=utf-8")
