from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()

GREEN_DOT_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="14" fill="#22c55e"/>
</svg>"""


@router.get("/favicon.ico", tags=["assets"], include_in_schema=False)
async def favicon():
    return Response(
        content=GREEN_DOT_SVG,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )
