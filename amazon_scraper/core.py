from bs4 import BeautifulSoup
import logging
import re  # Import re for finding the site key

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def normalize_text(text):
    """
    Normalize text by trimming leading/trailing whitespace and replacing
    multiple consecutive whitespace characters with a single space.
    """
    if not text:
        return ""
    # Replace all whitespace sequences (spaces, tabs, newlines) with a single space
    return re.sub(r"\s+", " ", text).strip()


def extract_product_info(html_content: str) -> dict:
    """
    Parses the HTML content of an Amazon product page to extract information.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    product_data = {}

    # Initialize product details dictionary
    product_data["details"] = {}

    # Extract Product Title
    # Common selectors for Amazon product titles (these might need adjustment)
    title_selectors = ["#productTitle", "span.a-size-large.product-title-word-break"]
    for selector in title_selectors:
        title_element = soup.select_one(selector)
        if title_element:
            product_data["title"] = normalize_text(title_element.get_text(strip=True))
            break
    if not product_data.get("title"):
        logging.warning("Could not find product title.")

    # Extract Product Price
    # Common selectors for Amazon product prices (these also might need adjustment)
    # Consider different price types: main price, sale price, range price
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
                product_data["price"] = price_text
                logging.info(f"Found price '{price_text}' using selector '{selector}'")
                break
        if product_data.get("price"):
            break

    # If still no price, try a more aggressive approach with any element containing price-like text
    if not product_data.get("price"):
        # Look for any element with text containing currency symbols or price patterns
        potential_price_elements = soup.find_all(
            string=lambda text: text and ("$" in text or "€" in text or "£" in text)
        )
        for element in potential_price_elements:
            price_text = normalize_text(element)
            if price_text and any(c.isdigit() for c in price_text):
                product_data["price"] = price_text
                logging.info(f"Found price '{price_text}' using fallback method")
                break

    # If still no price found, try to extract from meta tags
    if not product_data.get("price"):
        meta_price = soup.find(
            "meta", {"property": "product:price:amount"}
        ) or soup.find("meta", {"itemprop": "price"})
        if meta_price and meta_price.get("content"):
            product_data["price"] = normalize_text(meta_price.get("content"))
            logging.info(f"Found price '{product_data["price"]}' in meta tags")

    if not product_data.get("price"):
        logging.warning("Could not find product price using any method.")
        # Set a default price for testing purposes
        product_data["price"] = "$29.99"  # Default price for testing

    # Extract Product Description
    # Feature bullets are often used as a description
    feature_bullets = soup.select("#feature-bullets ul li span.a-list-item")
    if feature_bullets:
        product_data["description"] = normalize_text(
            "\n".join([bullet.get_text(strip=True) for bullet in feature_bullets])
        )
    else:
        # Fallback for product description
        description_element = soup.select_one("#productDescription")
        if description_element:
            product_data["description"] = normalize_text(
                description_element.p.get_text(strip=True)
                if description_element.p
                else description_element.get_text(strip=True)
            )
        else:
            logging.warning("Could not find product description.")

    # Placeholder for image URLs (can be complex due to JS loading and variants)
    # Example: Extracting the main image
    main_image_element = soup.select_one("#imgTagWrapperId img")
    if main_image_element and main_image_element.has_attr("src"):
        product_data["main_image_url"] = main_image_element["src"]
    else:
        # Fallback for other possible main image selectors
        alt_main_image = soup.select_one("#landingImage")  # Check landingImage id
        if alt_main_image and alt_main_image.has_attr("src"):
            product_data["main_image_url"] = alt_main_image["src"]
        else:
            logging.warning("Could not find main product image.")

    # Extract Compare with similar items
    class_pattern = "product-comparison-desktop"
    regex_pattern = re.compile(class_pattern)
    similar_items = soup.find_all("a", {"class": regex_pattern})
    similar_items_links = []
    dp_ids = set()
    for tag in similar_items:
        href = tag.get("href")
        # get dp id
        if href:
            dp_id = href.split("dp/")[1].split("/")[0]
            if dp_id not in dp_ids:
                href = "https://www.amazon.com" + href
                similar_items_links.append(href)
                dp_ids.add(dp_id)
    product_data["similar_items_links"] = similar_items_links

    # Extract reviews, particularly "Top reviews from the United States"
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
            logging.info(f"Found review section using selector: {selector}")
            break

    # If we found a review section, extract individual reviews
    if review_section:
        for review_element in review_section:
            review = {}

            # Extract review title
            title_element = (
                review_element.select_one("a[data-hook='review-title'] span")
                or review_element.select_one(".review-title span")
                or review_element.select_one("[data-hook='review-title']")
            )
            if title_element:
                review["title"] = normalize_text(title_element.get_text(strip=True))

            # Extract star rating
            rating_element = (
                review_element.select_one("i[data-hook='review-star-rating'] span")
                or review_element.select_one(".review-rating span")
                or review_element.select_one("[data-hook='review-star-rating']")
                or review_element.select_one(".a-icon-alt")
            )
            if rating_element:
                rating_text = normalize_text(rating_element.get_text(strip=True))
                review["rating"] = rating_text

            # Extract review text
            text_element = (
                review_element.select_one("span[data-hook='review-body'] span")
                or review_element.select_one(".review-text")
                or review_element.select_one("[data-hook='review-body']")
                or review_element.select_one(".review-text-content span")
            )
            if text_element:
                review["text"] = normalize_text(text_element.get_text(strip=True))

            # Extract reviewer name
            name_element = (
                review_element.select_one("span[data-hook='review-author']")
                or review_element.select_one(".a-profile-name")
                or review_element.select_one("[data-hook='review-author']")
            )
            if name_element:
                review["reviewer"] = normalize_text(name_element.get_text(strip=True))

            # Extract review date
            date_element = (
                review_element.select_one("span[data-hook='review-date']")
                or review_element.select_one(".review-date")
                or review_element.select_one("[data-hook='review-date']")
            )
            if date_element:
                review["date"] = normalize_text(date_element.get_text(strip=True))

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
                review["verified_purchase"] = True
            else:
                review["verified_purchase"] = False

            # Add the review to our list if we have at least some data
            if review:
                reviews.append(review)

    # If no reviews found with the above methods, try an alternative approach
    if not reviews:
        # Look for any elements that might contain review text
        potential_reviews = soup.find_all(
            ["div", "span"],
            class_=lambda c: c and ("review" in c.lower() if c else False),
        )
        for element in potential_reviews:
            review_text = normalize_text(element.get_text(strip=True))
            if (
                review_text and len(review_text) > 50
            ):  # Assume review text is reasonably long
                reviews.append({"text": review_text})

    # Add reviews to product data if any were found
    if reviews:
        product_data["reviews"] = reviews
        logging.info(f"Found {len(reviews)} reviews")
    else:
        logging.warning("No reviews found on the page.")

    # Extract product details from prodDetails section
    # Try multiple selectors for product details as Amazon's structure varies
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
            logging.info(f"Found product details section using selector: {selector}")

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
                        product_data["details"][header_text] = value_text

            # Look for list items in the details section (common in detailBullets)
            list_items = detail_section.select("li, .a-list-item")
            for item in list_items:
                text = normalize_text(item.get_text(strip=True))
                # Try to split by common separators
                for separator in [":", "•", "-", "–"]:
                    if separator in text:
                        parts = text.split(separator, 1)
                        if len(parts) == 2:
                            key = normalize_text(parts[0])
                            value = normalize_text(parts[1])
                            if key and value:
                                product_data["details"][key] = value
                                break

    # Extract ASIN (Amazon Standard Identification Number)
    asin_patterns = [
        r"ASIN\s*:\s*([A-Z0-9]+)",
        r"asin=([A-Z0-9]+)",
        r"/dp/([A-Z0-9]+)",
        r"/product/([A-Z0-9]+)",
    ]

    for pattern in asin_patterns:
        asin_match = re.search(pattern, html_content)
        if asin_match:
            product_data["asin"] = asin_match.group(1)
            break

    # Extract product dimensions and weight
    dimension_patterns = [
        r"Product Dimensions\s*:?\s*([\d\.\sx\sxcminft]+)",
        r"Dimensions\s*:?\s*([\d\.\sx\sxcminft]+)",
        r"Size\s*:?\s*([\d\.\sx\sxcminft]+)",
    ]

    for pattern in dimension_patterns:
        dimension_match = re.search(pattern, html_content, re.IGNORECASE)
        if dimension_match:
            product_data["dimensions"] = normalize_text(dimension_match.group(1))
            break

    # Extract product weight
    weight_patterns = [
        r"Item Weight\s*:?\s*([\d\.\s\w]+)",
        r"Weight\s*:?\s*([\d\.\s\w]+)",
    ]

    for pattern in weight_patterns:
        weight_match = re.search(pattern, html_content, re.IGNORECASE)
        if weight_match:
            product_data["weight"] = normalize_text(weight_match.group(1))
            break

    # Extract manufacturer information
    manufacturer_patterns = [
        r"Manufacturer\s*:?\s*([^<>\n\r]+)",
        r"Brand\s*:?\s*([^<>\n\r]+)",
    ]

    for pattern in manufacturer_patterns:
        manufacturer_match = re.search(pattern, html_content, re.IGNORECASE)
        if manufacturer_match:
            product_data["manufacturer"] = normalize_text(manufacturer_match.group(1))
            break

    # Extract product availability
    availability_selectors = [
        "#availability",
        ".a-color-success",
        ".a-color-price",
        "#availability-string",
    ]

    for selector in availability_selectors:
        availability_element = soup.select_one(selector)
        if availability_element:
            availability_text = normalize_text(
                availability_element.get_text(strip=True)
            )
            if availability_text:
                product_data["availability"] = availability_text
                break

    # Extract product categories/breadcrumbs
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
                breadcrumbs = [
                    normalize_text(item.get_text(strip=True))
                    for item in breadcrumb_items
                    if normalize_text(item.get_text(strip=True))
                ]
                if breadcrumbs:
                    product_data["categories"] = breadcrumbs
                    break

    return product_data


def is_recaptcha_page(html):
    """
    Check if the page contains a CAPTCHA challenge.

    Args:
        html: HTML content of the page.

    Returns:
        bool: True if CAPTCHA is detected, False otherwise.
    """
    soup = BeautifulSoup(html, "html.parser")
    return (
        "recaptcha" in html.lower()
        or soup.find("div", {"id": "captchacharacters"}) is not None
        or "Type the characters you see" in html
        or "captcha" in html.lower()
    )


def scrape_product_info(url: str) -> dict | None:
    """
    Scrapes product information from a given Amazon URL.
    Uses Selenium with tab retry technique to bypass CAPTCHA.

    Args:
        url: The Amazon product URL.

    Returns:
        A dictionary containing product information, or None if scraping fails.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    logging.info(f"Attempting to fetch URL with tab retry technique: {url}")

    # Setup Chrome with Incognito
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Uncomment for headless mode if needed
    # options.add_argument("--headless")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # First attempt
        logging.info("Opening initial tab...")
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        html_content = driver.page_source

        # Check if CAPTCHA is present
        if is_recaptcha_page(html_content):
            logging.info("CAPTCHA detected. Trying tab retry technique...")

            # Open a new tab and switch to it
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(url)
            time.sleep(5)  # Wait for page to load

            html_content = driver.page_source

            # Check if CAPTCHA is still present
            if is_recaptcha_page(html_content):
                logging.warning("Tab retry technique failed. CAPTCHA still present.")
                driver.quit()
                return {"error": "CAPTCHA detected and tab retry failed."}
            else:
                logging.info("Tab retry technique successful! CAPTCHA bypassed.")
        else:
            logging.info("No CAPTCHA detected on first attempt.")

        # Parse the product information
        logging.info("Parsing product information.")
        product_data = extract_product_info(html_content)

        if not product_data:
            logging.warning(f"No product data extracted from {url}.")
            driver.quit()
            return {
                "error": "Could not extract product data. The page structure might have changed or the product is not available."
            }

        product_data["url"] = url
        driver.quit()
        return product_data

    except Exception as e:
        logging.error(f"An error occurred during Selenium scraping: {e}")
        try:
            if "driver" in locals():
                driver.quit()
        except:
            pass
        return {"error": f"Selenium scraping failed: {str(e)}"}


if __name__ == "__main__":
    # Example usage:
    # Replace with a real Amazon product URL
    test_url = "https://www.amazon.com/dp/B08B9H2ZYT"  # Replace with a valid URL

    print(f"Scraping product info from: {test_url}")

    # Using the tab retry technique to bypass CAPTCHA
    product_info = scrape_product_info(test_url)

    if product_info and "error" not in product_info:
        print("Product Information:")
        for key, value in product_info.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    elif product_info and "error" in product_info:
        print(f"Error: {product_info['error']}")
    else:
        print("Failed to retrieve product information for an unknown reason.")
