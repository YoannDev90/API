from logging import getLogger
from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()


import httpx, xml.dom.minidom

@router.get("/pretty-xml", tags=["format"])
async def pretty_xml(url: str = Query(..., description="XML URL")):
    if not url.startswith(("http://", "https://")): url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            resp = await c.get(url)
        dom = xml.dom.minidom.parseString(resp.text)
        from fastapi.responses import Response
        return Response(content=dom.toprettyxml(indent="  "), media_type="application/xml; charset=utf-8")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
