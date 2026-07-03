from logging import getLogger

from fastapi import APIRouter, HTTPException, Query


logger = getLogger("api-proxy")
router = APIRouter()




import os

@router.get("/screenshot", tags=["utils"])
async def screenshot(url: str = Query(..., description="Website URL")):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    from fastapi.responses import Response
    try:
        from playwright.async_api import async_playwright
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.join(os.path.dirname(__file__), "..", ".pw-browsers"))
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            await page.goto(url, wait_until="networkidle", timeout=30000)
            png = await page.screenshot(type="png", full_page=False)
            await browser.close()
        return Response(content=png, media_type="image/png")
    except Exception as e:
        logger.error(f"Screenshot failed for {url}: {e}")
        raise HTTPException(status_code=502, detail=f"Screenshot failed: {e}")

