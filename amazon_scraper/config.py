"""
Configuration settings for the Amazon scraper.

This module contains default configuration values that can be imported and
optionally overridden by users of the library.
"""

from pathlib import Path

# ---------------- Browser settings ----------------
HEADLESS: bool = True
USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)
VIEWPORT: dict = {"width": 1280, "height": 800}
LOCALE: str = "en-US"
TIMEZONE_ID: str = "America/New_York"
NAV_TIMEOUT_MS: int = 30_000
LAUNCH_ARGS: list[str] = [
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--no-sandbox",
]

# ---------------- Scraper settings ----------------
MAX_RETRIES: int = 5
RETRY_DELAY_SEC: float = 2.0
PAGE_TIMEOUT_MS: int = 20_000
CAPTCHA_MAX_RETRIES: int = 5
DELAY_AFTER_LOAD_SEC: float = 2.0

# ---------------- Extraction tweaks ----------------
TITLE_SELECTORS: list[str] = [
    "#productTitle",
    "span.a-size-large.product-title-word-break",
]
PRICE_SELECTORS: list[str] = [
    "span.a-price.a-text-price.a-size-medium span.a-offscreen",
    "span.a-price.apexPriceToPay span.a-offscreen",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    "#priceblock_saleprice",
    "span.priceToPay span.a-offscreen",
    "div#corePrice_feature_div span.a-offscreen",
    "div#olp_feature_div span.a-color-price",
    ".a-price .a-offscreen",
    "#price",
    "#price_inside_buybox",
    "#newBuyBoxPrice",
    "#tp_price_block_total_price_ww .a-offscreen",
    ".a-section .a-price .a-offscreen",
    "#corePrice_desktop .a-offscreen",
]
MIN_REVIEW_LENGTH: int = 50

# ---------------- Output / logging ----------------
SAVE_HTML: bool = False
OUTPUT_DIR: Path = Path("./tmp/html")
LOG_LEVEL: str = "INFO"  # "DEBUG", "INFO", etc.
LOG_FILE: Path = Path("./logs/scraper.log")
LOG_ROTATE_MB: int = 10
