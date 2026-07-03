from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from pydantic import BaseModel, Field

class TranslateInput(BaseModel):
    text: str = Field(..., description="Text to translate")
    source: str = Field(default="auto")
    target: str = Field(default="en")

@router.post("/translate", tags=["utils"])
async def translate(body: TranslateInput):
    try:
        from deep_translator import GoogleTranslator
        t = GoogleTranslator(source=body.source, target=body.target)
        result = t.translate(body.text)
        return {"code": "200", "source": body.source, "target": body.target, "text": body.text, "translated": result}
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=502, detail=f"Translation failed: {e}")

