import asyncio
import logging
from typing import Optional
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)


class BrowserManager:
    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._lock = asyncio.Lock()

    async def initialize(self):
        async with self._lock:
            if self._browser and self._browser.is_connected():
                return
            if self._playwright:
                await self.close()
            logging.info("Starting Playwright")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--disable-gpu", "--no-sandbox"],
            )
            self._context = await self._browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                timezone_id="America/New_York",
                has_touch=False,
                java_script_enabled=True,
                ignore_https_errors=True,
            )
            self._context.set_default_navigation_timeout(30_000)

            # dummy tab to keep context alive
            page = await self._context.new_page()
            await page.goto("about:blank")
            logging.info("BrowserManager ready")

    async def get_page(self) -> Page:
        await self.initialize()
        return await self._context.new_page()

    async def close(self):
        async with self._lock:
            if self._context:
                await self._context.close()
                self._context = None
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            logging.info("BrowserManager shut down")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


# module-level singleton
_manager_lock = asyncio.Lock()
_browser_manager: Optional[BrowserManager] = None


async def get_browser_manager() -> BrowserManager:
    global _browser_manager
    async with _manager_lock:
        if _browser_manager is None:
            _browser_manager = BrowserManager()
            await _browser_manager.initialize()
    return _browser_manager
