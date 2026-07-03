from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




from fastapi.responses import Response

@router.get("/qr", tags=["utils"])
async def qr_code(text: str = Query(..., description="Text to encode"),
                  size: int = Query(default=300, ge=50, le=2000)):
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.make(text)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        png = buf.getvalue()
        return Response(content=png, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"QR failed: {e}")

