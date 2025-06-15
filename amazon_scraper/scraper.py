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
from amazon_scraper.browser_manager import get_browser_manager, BrowserManager


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
    similar_items_links = extract_similar_items(html_content)

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
    url: str, browser_manager: Optional[BrowserManager] = None
) -> Optional[ProductInfo]:
    """
    Scrapes product information from a given Amazon URL using Playwright.
    Uses the provided browser_manager or gets one from the browser manager singleton.

    Args:
        url: The Amazon product URL
        browser_manager: Optional BrowserManager instance to use (if not provided, will get from get_browser_manager())

    Returns:
        ProductInfo object containing product information, or None if scraping fails
    """
    try:
        logging.info(f"Scraping product info from {url}")

        # Get browser manager if not provided
        if browser_manager is None:
            browser_manager = await get_browser_manager()

        # Get a page from the browser manager
        page = await browser_manager.get_page()

        # Function to get page content with retry logic
        async def get_page_content_with_retry(
            current_page: Page,
            old_page: Optional[Page] = None,
            retry_count: int = 0,
            max_retries: int = 5,
        ):
            try:
                # Use 'domcontentloaded' instead of 'networkidle' which is more reliable for Amazon
                # and reduce timeout to avoid long waits
                await current_page.goto(
                    url, wait_until="domcontentloaded", timeout=20000
                )

                # Close old page after navigation if provided
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

                    # Get a new page from browser manager
                    new_page = await browser_manager.get_page()

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

                # Close current page and get a new one from browser manager
                await current_page.close()
                new_page = await browser_manager.get_page()

                # Wait a bit before retrying
                await asyncio.sleep(2)
                return await get_page_content_with_retry(
                    new_page, None, retry_count + 1, max_retries
                )

        try:
            # Get the page content with retry logic
            html_content, page = await get_page_content_with_retry(page, None)
        except Exception as e:
            logging.error(f"Unexpected error during page content retrieval: {str(e)}")
            await page.close()
            return None

        if html_content is None:
            logging.error(f"Failed to get content from {url}")
            await page.close()
            return None

        # Extract product information
        product_info = extract_product_info(html_content)
        logging.info(f"Successfully extracted product info for {url}")

        # Close the page when done
        await page.close()

        return product_info

    except Exception as e:
        logging.error(f"Error scraping product info from {url}: {str(e)}")
        return None
