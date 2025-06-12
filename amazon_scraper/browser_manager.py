"""
Browser manager for handling Playwright browser instances.
"""

import logging
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page


class BrowserManager:
    """
    Manages a Playwright browser instance with a dummy tab to keep the session alive.
    """

    def __init__(self):
        self._browser: Optional[Browser] = None
        self._dummy_page: Optional[Page] = None
        self._playwright = None
        self._lock = asyncio.Lock()

    async def initialize(self):
        """
        Initialize the browser manager by launching a browser in incognito mode
        with a dummy tab to keep the session alive.
        """
        if self._browser is not None:
            return

        async with self._lock:
            if self._browser is not None:  # Double-check after acquiring lock
                return

            try:
                logging.info("Initializing browser manager")
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                )

                # Create a new incognito browser context
                context = await self._browser.new_context()

                # Create a dummy page to keep the browser session alive
                self._dummy_page = await context.new_page()
                await self._dummy_page.goto("about:blank")
                logging.info("Browser manager initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing browser manager: {str(e)}")
                await self.close()
                raise

    async def get_browser(self) -> Browser:
        """
        Get the browser instance. Initialize if not already done.

        Returns:
            Browser: The Playwright browser instance
        """
        if self._browser is None:
            await self.initialize()
        return self._browser

    async def close(self):
        """
        Close the browser and clean up resources.
        """
        if self._browser:
            try:
                await self._browser.close()
                logging.info("Browser closed")
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")
            finally:
                self._browser = None
                self._dummy_page = None

        if self._playwright:
            try:
                await self._playwright.stop()
                logging.info("Playwright stopped")
            except Exception as e:
                logging.error(f"Error stopping playwright: {str(e)}")
            finally:
                self._playwright = None


# Singleton instance
_browser_manager = None


async def get_browser_manager() -> BrowserManager:
    """
    Get the singleton browser manager instance.

    Returns:
        BrowserManager: The browser manager instance
    """
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
        await _browser_manager.initialize()
    return _browser_manager
