"""
Functions for scraping Amazon product pages.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from playwright.async_api import Browser, Page

from amazon_scraper.models import ProductInfo, ProductDetails, Review
from amazon_scraper.extractors import (
    extract_title,
    extract_price,
    extract_description,
    extract_main_image,
    extract_similar_items,
    extract_reviews,
    extract_product_details,
)
from amazon_scraper.captcha import is_recaptcha_page
from amazon_scraper.browser_manager import get_browser_manager


def extract_product_info(html_content: str) -> ProductInfo:
    """
    Parses the HTML content of an Amazon product page to extract information.

    Args:
        html_content: HTML content of the Amazon product page

    Returns:
        ProductInfo object containing extracted product information
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract basic product information
    title = extract_title(soup)
    price = extract_price(soup)
    description = extract_description(soup)
    main_image_url = extract_main_image(soup)
    similar_items_links = extract_similar_items(soup)

    # Extract reviews
    reviews = extract_reviews(soup)

    # Extract product details
    details = extract_product_details(soup, html_content)

    # Create and return the ProductInfo object
    return ProductInfo(
        title=title,
        price=price,
        description=description,
        main_image_url=main_image_url,
        similar_items_links=similar_items_links,
        reviews=reviews,
        details=details,
    )


async def scrape_product_info(
    url: str, browser: Optional[Browser] = None
) -> Optional[ProductInfo]:
    """
    Scrapes product information from a given Amazon URL using Playwright.
    Uses the provided browser or gets one from the browser manager.

    Args:
        url: The Amazon product URL
        browser: Optional browser instance to use (if not provided, will get from browser_manager)

    Returns:
        ProductInfo object containing product information, or None if scraping fails
    """
    try:
        logging.info(f"Scraping product info from {url}")

        # Get browser from manager if not provided
        if browser is None:
            browser_manager = await get_browser_manager()
            browser = await browser_manager.get_browser()

        # Create a new context for this scrape with more realistic browser settings
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="America/New_York",
            has_touch=False,
            java_script_enabled=True,
            ignore_https_errors=True,
        )

        # Create a new page
        page = await context.new_page()

        # Function to get page content with retry logic
        async def get_page_content_with_retry(
            current_page, old_page, retry_count=0, max_retries=5
        ):
            try:
                # Use 'domcontentloaded' instead of 'networkidle' which is more reliable for Amazon
                # and reduce timeout to avoid long waits
                await current_page.goto(
                    url, wait_until="domcontentloaded", timeout=20000
                )

                # Close old page after navigation
                if old_page:
                    await old_page.close()

                # Add a small delay to allow critical content to load
                await asyncio.sleep(2)
                html_content = await current_page.content()

                # Check if we hit a CAPTCHA
                if is_recaptcha_page(html_content):
                    logging.warning(
                        f"CAPTCHA detected (attempt {retry_count+1}/{max_retries}), retrying..."
                    )

                    if retry_count >= max_retries:
                        logging.error(
                            f"Failed to bypass CAPTCHA after {max_retries} attempts"
                        )
                        return None, current_page

                    new_page = await context.new_page()

                    # Wait a bit before retrying
                    await asyncio.sleep(2)
                    return await get_page_content_with_retry(
                        new_page, current_page, retry_count + 1, max_retries
                    )

                return html_content, current_page
            except Exception as e:
                logging.error(
                    f"Error loading page (attempt {retry_count+1}/{max_retries}): {str(e)}"
                )

                if retry_count >= max_retries:
                    logging.error(f"Failed to load page after {max_retries} attempts")
                    return None, current_page

                # Close current page and open a new one to retry
                await current_page.close()
                new_page = await context.new_page()

                # Wait a bit before retrying
                await asyncio.sleep(2)
                return await get_page_content_with_retry(
                    new_page, retry_count + 1, max_retries
                )

        try:
            # Get the page content with retry logic
            html_content, page = await get_page_content_with_retry(page, None)
        except Exception as e:
            logging.error(f"Unexpected error during page content retrieval: {str(e)}")
            await context.close()
            return None

        if html_content is None:
            logging.error(f"Failed to get content from {url}")
            await context.close()
            return None

        # Extract product information
        product_info = extract_product_info(html_content)
        logging.info(f"Successfully extracted product info for {url}")

        # Close the context (which closes all pages except the dummy page)
        await context.close()

        return product_info

    except Exception as e:
        logging.error(f"Error scraping product info from {url}: {str(e)}")
        return None
