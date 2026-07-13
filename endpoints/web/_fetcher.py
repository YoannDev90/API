"""Shared fetcher using Scrapling's DynamicFetcher (bypasses Cloudflare, renders JS)."""
import asyncio
import logging
import os

logger = logging.getLogger("api-proxy")

_playwright_configured = False


def _ensure_playwright():
    global _playwright_configured
    if not _playwright_configured:
        pw_path = os.path.join(os.path.dirname(__file__), "..", "..", ".pw-browsers")
        if os.path.exists(pw_path):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = pw_path
        _playwright_configured = True


async def fetch_page(url: str) -> str:
    """Fetch a page using DynamicFetcher, returns HTML content."""
    _ensure_playwright()
    from scrapling.fetchers import DynamicFetcher

    loop = asyncio.get_event_loop()
    try:
        page = await loop.run_in_executor(
            None, lambda: DynamicFetcher.fetch(url, headless=True, network_idle=True)
        )
        return page.html_content
    except Exception as e:
        logger.error(f"DynamicFetcher failed for {url}: {e}")
        raise
