from logging import getLogger
from fastapi import APIRouter


logger = getLogger("api-proxy")
router = APIRouter()


from pydantic import BaseModel, Field

class FindReplaceInput(BaseModel):
    text: str = Field(..., description="Input text")
    find: str = Field(..., description="Text to find")
    replace: str = Field(default="", description="Replacement text")
    regex: bool = Field(default=False, description="Use regex")

@router.post("/text/find-replace", tags=["text"])
async def text_find_replace(body: FindReplaceInput):
    import re
    if body.regex:
        result = re.sub(body.find, body.replace, body.text)
        count = len(re.findall(body.find, body.text))
    else:
        result = body.text.replace(body.find, body.replace)
        count = body.text.count(body.find)
    return {"code": "200", "result": result, "replacements": count}
