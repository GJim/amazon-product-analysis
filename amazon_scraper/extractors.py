"""
Specialized extractors for different parts of Amazon product pages.
Each extractor is focused on a specific type of data to extract.
"""

import re
import logging
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup

from amazon_scraper import config

from amazon_scraper.extraction_utils import (
    normalize_text,
    extract_text_from_element,
    extract_elements,
    extract_with_regex,
    find_in_html,
    extract_key_value_from_text,
)
from amazon_scraper.models import Review, ProductDetails


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract the product title from the page.

    Args:
        soup: BeautifulSoup object of the product page

    Returns:
        Product title if found, None otherwise
    """
    title_selectors = getattr(config, 'TITLE_SELECTORS', ["#productTitle", "span.a-size-large.product-title-word-break"])
    title = extract_text_from_element(soup, title_selectors)
    if not title:
        logging.warning("Could not find product title.")
    return title


def extract_price(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract the product price from the page using multiple methods.

    Args:
        soup: BeautifulSoup object of the product page

    Returns:
        Product price if found, None otherwise
    """
    # Use price selectors from config or fall back to defaults if empty
    price_selectors = getattr(config, 'PRICE_SELECTORS', [])
    if not price_selectors:
        # Common selectors for Amazon product prices
        price_selectors = [
            "span.a-price.a-text-price.a-size-medium span.a-offscreen",  # Standard price
            "span.a-price.apexPriceToPay span.a-offscreen",  # Another common price format
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "#priceblock_saleprice",
            "span.priceToPay span.a-offscreen",  # For some formats
            "div#corePrice_feature_div span.a-offscreen",  # More specific price block
            "div#olp_feature_div span.a-color-price",  # Used price or other offers
            ".a-price .a-offscreen",  # Generic a-price class with a-offscreen
            "#price",  # Simple price ID
            "#price_inside_buybox",  # Price inside buy box
            "#newBuyBoxPrice",  # New buy box price
            "#tp_price_block_total_price_ww .a-offscreen",  # Total price block
            ".a-section .a-price .a-offscreen",  # Price within a section
            "#corePrice_desktop .a-offscreen",  # Desktop core price
        ]

    # Try all selectors
    for selector in price_selectors:
        price_elements = soup.select(selector)  # Get all matching elements
        for price_element in price_elements:
            price_text = normalize_text(price_element.get_text(strip=True))
            if price_text and any(
                c.isdigit() for c in price_text
            ):  # Ensure it contains at least one digit
                return price_text

    # If still no price, try a more aggressive approach with any element containing price-like text
    potential_price_elements = soup.find_all(
        string=lambda text: text and ("$" in text or "€" in text or "£" in text)
    )
    for element in potential_price_elements:
        price_text = normalize_text(element)
        if price_text and any(c.isdigit() for c in price_text):
            return price_text

    # If still no price found, try to extract from meta tags
    meta_price = soup.find("meta", {"property": "product:price:amount"}) or soup.find(
        "meta", {"itemprop": "price"}
    )
    if meta_price and meta_price.get("content"):
        price_text = normalize_text(meta_price.get("content"))
        return price_text

    logging.warning("Could not find product price using any method.")
    return None


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract the product description from the page.

    Args:
        soup: BeautifulSoup object of the product page

    Returns:
        Product description if found, None otherwise
    """
    # Feature bullets are often used as a description
    feature_bullets = soup.select("#feature-bullets ul li span.a-list-item")
    if feature_bullets:
        return normalize_text(
            "\n".join([bullet.get_text(strip=True) for bullet in feature_bullets])
        )

    # Fallback for product description
    description_element = soup.select_one("#productDescription")
    if description_element:
        return normalize_text(
            description_element.p.get_text(strip=True)
            if description_element.p
            else description_element.get_text(strip=True)
        )

    logging.warning("Could not find product description.")
    return None


def extract_main_image(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract the main product image URL from the page.

    Args:
        soup: BeautifulSoup object of the product page

    Returns:
        Main image URL if found, None otherwise
    """
    main_image_element = soup.select_one("#imgTagWrapperId img")
    if main_image_element and main_image_element.has_attr("src"):
        return main_image_element["src"]

    # Fallback for other possible main image selectors
    alt_main_image = soup.select_one("#landingImage")  # Check landingImage id
    if alt_main_image and alt_main_image.has_attr("src"):
        return alt_main_image["src"]

    logging.warning("Could not find main product image.")
    return None


def extract_similar_items(html_content: str) -> List[str]:
    """
    Extract unique Amazon product links of the form:
      - https://www.amazon.com/dp/<ASIN>/...
      - https://www.amazon.com/<product-title>/dp/<ASIN>/...
    and normalize them to:
      https://www.amazon.com/dp/<ASIN>

    ASINs consist of 10 uppercase letters and digits.

    Args:
        html_content: Raw HTML as a string.

    Returns:
        A list of normalized, deduplicated product URLs.
    """
    # Match either pattern, capture the 10-char ASIN
    pattern = re.compile(
        r"https?://www\.amazon\.com"  # scheme + host
        r"(?:/[^/]+)?"  # optional product-title segment
        r"/dp/([A-Z0-9]{10})"  # the /dp/ASIN part
        r'(?:/[^"\s]*)?',  # optional trailing path
        re.IGNORECASE,
    )

    seen = set()
    result = []
    for match in pattern.finditer(html_content):
        asin = match.group(1).upper()
        if asin not in seen:
            seen.add(asin)
            result.append(f"https://www.amazon.com/dp/{asin}")
    return result


def extract_reviews(soup: BeautifulSoup) -> List[Review]:
    """
    Extract product reviews from the page.

    Args:
        soup: BeautifulSoup object of the product page

    Returns:
        List of Review objects
    """
    reviews = []

    # Common selectors for Amazon reviews
    review_section_selectors = [
        "#customer-reviews-content",
        "div[data-hook='review']",
        ".review",
        "#cm-cr-dp-review-list .review",
        ".a-section.review",
        "div[data-hook='review-section']",
    ]

    # Try to find the review section
    review_section = None
    for selector in review_section_selectors:
        sections = soup.select(selector)
        if sections:
            review_section = sections
            break

    # If we found a review section, extract individual reviews
    if review_section:
        for review_element in review_section:
            review_data = {}

            # Extract review title
            title_element = (
                review_element.select_one("a[data-hook='review-title'] span")
                or review_element.select_one(".review-title span")
                or review_element.select_one("[data-hook='review-title']")
            )
            if title_element:
                review_data["title"] = normalize_text(
                    title_element.get_text(strip=True)
                )

            # Extract star rating
            rating_element = (
                review_element.select_one("i[data-hook='review-star-rating'] span")
                or review_element.select_one(".review-rating span")
                or review_element.select_one("[data-hook='review-star-rating']")
                or review_element.select_one(".a-icon-alt")
            )
            if rating_element:
                rating_text = normalize_text(rating_element.get_text(strip=True))
                # extract rating as float
                rating_match = re.search(r"(\d*\.\d+|\d+)", rating_text)
                review_data["rating"] = "0"
                if rating_match:
                    review_data["rating"] = rating_match.group()

            # Extract review text
            text_element = (
                review_element.select_one("span[data-hook='review-body'] span")
                or review_element.select_one(".review-text")
                or review_element.select_one("[data-hook='review-body']")
                or review_element.select_one(".review-text-content span")
            )
            if text_element:
                review_data["text"] = normalize_text(text_element.get_text(strip=True))

            # Extract reviewer name
            name_element = (
                review_element.select_one("span[data-hook='review-author']")
                or review_element.select_one(".a-profile-name")
                or review_element.select_one("[data-hook='review-author']")
            )
            if name_element:
                review_data["reviewer"] = normalize_text(
                    name_element.get_text(strip=True)
                )

            # Extract review date
            date_element = (
                review_element.select_one("span[data-hook='review-date']")
                or review_element.select_one(".review-date")
                or review_element.select_one("[data-hook='review-date']")
            )
            if date_element:
                review_data["date"] = normalize_text(date_element.get_text(strip=True))

            # Extract verified purchase status
            verified_element = (
                review_element.select_one("span[data-hook='avp-badge']")
                or review_element.select_one(".a-color-state")
                or review_element.select_one("[data-hook='avp-badge']")
            )
            if (
                verified_element
                and "verified purchase"
                in normalize_text(verified_element.get_text(strip=True)).lower()
            ):
                review_data["verified_purchase"] = True
            else:
                review_data["verified_purchase"] = False

            # Add the review to our list if we have at least some data
            if review_data:
                if review_data["rating"] != "0":
                    reviews.append(Review(**review_data))

    # If no reviews found with the above methods, try an alternative approach
    if not reviews:
        # Look for any elements that might contain review text
        potential_reviews = soup.find_all(
            ["div", "span"],
            class_=lambda c: c and ("review" in c.lower() if c else False),
        )
        for element in potential_reviews:
            review_text = normalize_text(element.get_text(strip=True))
            min_review_length = getattr(config, 'MIN_REVIEW_LENGTH', 50)
            if (
                review_text and len(review_text) > min_review_length
            ):  # Assume review text is reasonably long
                reviews.append(Review(text=review_text))

    if len(reviews) == 0:
        logging.warning("Could not find any reviews.")
    return reviews


def extract_product_details(soup: BeautifulSoup, html_content: str) -> ProductDetails:
    """
    Extract detailed product information including specifications.

    Args:
        soup: BeautifulSoup object of the product page
        html_content: Raw HTML content for regex-based extraction

    Returns:
        ProductDetails object with extracted information
    """

    # Extract availability
    availability_selectors = [
        "#availability",
        ".a-color-success",
        ".a-color-price",
        "#availability-string",
    ]
    availability = extract_text_from_element(soup, availability_selectors)

    # Extract categories/breadcrumbs
    categories = []
    breadcrumb_selectors = [
        "#wayfinding-breadcrumbs_feature_div",
        ".a-breadcrumb",
        "#nav-subnav",
    ]

    for selector in breadcrumb_selectors:
        breadcrumb_element = soup.select_one(selector)
        if breadcrumb_element:
            breadcrumb_items = breadcrumb_element.select("a")
            if breadcrumb_items:
                categories = [
                    normalize_text(item.get_text(strip=True))
                    for item in breadcrumb_items
                    if normalize_text(item.get_text(strip=True))
                ]
                break

    # Extract product specifications
    specifications = {}
    detail_selectors = [
        "#prodDetails",
        "#productDetails",
        "#detailBullets",
        "#technicalDetails",
        ".detail-bullets",
        "#detailBulletsWrapper_feature_div",
        "#productDescription",
        "#feature-bullets",
        "#technicalSpecifications_feature_div",
        ".a-section.a-spacing-small.a-spacing-top-small",
    ]

    # Extract product details
    for selector in detail_selectors:
        detail_section = soup.select_one(selector)
        if detail_section:
            # Look for table rows in the details section
            rows = detail_section.select("tr")
            for row in rows:
                # Extract the header and value from the row
                header = row.select_one("th")
                value = row.select_one("td")
                if header and value:
                    header_text = normalize_text(header.get_text(strip=True))
                    value_text = normalize_text(value.get_text(strip=True))
                    if header_text and value_text:
                        # normalize header to lower case
                        specifications[header_text.lower()] = value_text

            # Look for list items in the details section (common in detailBullets)
            list_items = detail_section.select("li, .a-list-item")
            for item in list_items:
                text = normalize_text(item.get_text(strip=True))
                key, value = extract_key_value_from_text(text)
                if key and value:
                    # normalize key to lower case
                    specifications[key.lower()] = value

    # Create and return the ProductDetails object
    return ProductDetails(
        availability=availability, categories=categories, specifications=specifications
    )
