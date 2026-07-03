from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




@router.get("/csp", tags=["tools"])
async def csp_generator(default_src: str = Query(default="'self'"), script_src: str = Query(default="'self'"),
                        style_src: str = Query(default="'self'"), img_src: str = Query(default="'self' data:"),
                        connect_src: str = Query(default="'self'"), font_src: str = Query(default="'self'"),
                        frame_src: str = Query(default=""), report_uri: str = Query(default="")):
    dirs = []
    for n, v in [("default-src",default_src),("script-src",script_src),("style-src",style_src),("img-src",img_src),
                  ("connect-src",connect_src),("font-src",font_src),("frame-src",frame_src)]:
        if v: dirs.append(f"{n} {v}")
    if report_uri: dirs.append(f"report-uri {report_uri}")
    csp = "; ".join(dirs)
    return {"code": "200", "csp": csp, "header": f"Content-Security-Policy: {csp}"}

