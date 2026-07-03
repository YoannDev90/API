from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class MarkdownInput(BaseModel):
    text: str = Field(..., description="Markdown content")

@router.post("/markdown", tags=["utils"])
async def markdown_to_html(body: MarkdownInput):
    try:
        import markdown as md
        html = md.markdown(body.text, extensions=["fenced_code", "tables"])
        return {"code": "200", "html": html}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Markdown failed: {e}")

