import requests
from bs4 import BeautifulSoup
from amazon_scraper.utils import solve_recaptcha
import logging
import re # Import re for finding the site key

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Placeholder for Amazon's reCAPTCHA site key if it's static and known.
# Otherwise, it needs to be extracted from the page.
AMAZON_RECAPTCHA_SITE_KEY_REGEX = r'data-sitekey="([^"]+)"' # Example regex

def extract_product_info(html_content: str) -> dict:
    """
    Parses the HTML content of an Amazon product page to extract information.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    product_data = {}

    # Extract Product Title
    # Common selectors for Amazon product titles (these might need adjustment)
    title_selectors = ['#productTitle', 'span.a-size-large.product-title-word-break']
    for selector in title_selectors:
        title_element = soup.select_one(selector)
        if title_element:
            product_data['title'] = title_element.get_text(strip=True)
            break
    if not product_data.get('title'):
        logging.warning("Could not find product title.")

    # Extract Product Price
    # Common selectors for Amazon product prices (these also might need adjustment)
    # Consider different price types: main price, sale price, range price
    price_selectors = [
        'span.a-price.a-text-price.a-size-medium span.a-offscreen', # Standard price
        'span.a-price.apexPriceToPay span.a-offscreen', # Another common price format
        '#priceblock_ourprice',
        '#priceblock_dealprice',
        '#priceblock_saleprice',
        'span.priceToPay span.a-offscreen', # For some formats
        'div#corePrice_feature_div span.a-offscreen', # More specific price block
        'div#olp_feature_div span.a-color-price' # Used price or other offers
    ]
    for selector in price_selectors:
        price_element = soup.select_one(selector)
        if price_element:
            price_text = price_element.get_text(strip=True)
            # Clean up price text (e.g., remove currency symbols if needed, convert to float)
            # This cleaning might need to be more robust depending on Amazon's formats
            product_data['price'] = price_text
            break
    if not product_data.get('price'):
        logging.warning("Could not find product price.")

    # Extract Product Description
    # Description can be in various places, often under '#productDescription'
    description_element = soup.select_one('#productDescription')
    if description_element:
        product_data['description'] = description_element.p.get_text(strip=True) if description_element.p else description_element.get_text(strip=True)
    else:
        # Fallback for feature bullets if main description is not found
        feature_bullets = soup.select('#feature-bullets ul li span.a-list-item')
        if feature_bullets:
            product_data['description'] = "\n".join([bullet.get_text(strip=True) for bullet in feature_bullets])
        else:
            logging.warning("Could not find product description.")

    # Placeholder for image URLs (can be complex due to JS loading and variants)
    # Example: Extracting the main image
    main_image_element = soup.select_one('#imgTagWrapperId img')
    if main_image_element and main_image_element.has_attr('src'):
        product_data['main_image_url'] = main_image_element['src']
    else:
        # Fallback for other possible main image selectors
        alt_main_image = soup.select_one('#landingImage') # Check landingImage id
        if alt_main_image and alt_main_image.has_attr('src'):
             product_data['main_image_url'] = alt_main_image['src']
        else:
            logging.warning("Could not find main product image.")


    return product_data

def scrape_product_info(url: str, captcha_api_key: str = None) -> dict | None:
    """
    Scrapes product information from a given Amazon URL.
    Handles reCAPTCHA if encountered.

    Args:
        url: The Amazon product URL.
        captcha_api_key: The API key for the CAPTCHA solving service.
                         Required if a CAPTCHA is encountered.

    Returns:
        A dictionary containing product information, or None if scraping fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1", # Do Not Track Request Header
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        logging.info(f"Attempting to fetch URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        html_content = response.text

        # Basic reCAPTCHA detection: Check for common reCAPTCHA elements or messages.
        # This is a simplified check and might need to be made more robust.
        if "reCAPTCHA" in html_content or "captcha" in html_content.lower():
            logging.info("reCAPTCHA detected on the page.")
            if not captcha_api_key:
                logging.error("CAPTCHA detected, but no API key provided.")
                return {"error": "CAPTCHA detected, but no API key provided."}

            # Attempt to extract site key from the page
            # This is a common way site keys are embedded, but can vary
            site_key_match = re.search(AMAZON_RECAPTCHA_SITE_KEY_REGEX, html_content)
            if site_key_match:
                site_key = site_key_match.group(1)
                logging.info(f"Extracted site key: {site_key}")

                # Call the CAPTCHA solving utility
                captcha_solution = solve_recaptcha(site_key, url, captcha_api_key)

                if captcha_solution:
                    logging.info("CAPTCHA solved successfully. Retrying request with CAPTCHA solution (not implemented yet).")
                    # Here you would typically resubmit the form or request with the CAPTCHA token.
                    # For Amazon, this might involve more complex interactions if the CAPTCHA
                    # is part of a form submission. For now, we'll just log it.
                    # This part needs to be adapted based on how Amazon handles CAPTCHA verification (e.g., form data).
                    # For a simple page block, sometimes just solving it and retrying the request might work,
                    # but often it's tied to a specific action.

                    # For now, we'll try to re-fetch the page, assuming solving the CAPTCHA
                    # on a previous step might grant access. This is a simplification.
                    # response = requests.get(url, headers=headers, timeout=10)
                    # response.raise_for_status()
                    # html_content = response.text
                    logging.warning("CAPTCHA was solved, but direct re-fetch without form submission might not bypass protection. Product info might be incomplete.")

                else:
                    logging.error("Failed to solve CAPTCHA.")
                    return {"error": "Failed to solve CAPTCHA."}
            else:
                logging.error("CAPTCHA detected, but could not extract site key.")
                return {"error": "CAPTCHA detected, but could not extract site key."}

        logging.info("Parsing product information.")
        product_data = extract_product_info(html_content)

        if not product_data:
            logging.warning(f"No product data extracted from {url}.")
            return {"error": "Could not extract product data. The page structure might have changed or the product is not available."}

        product_data['url'] = url
        return product_data

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e} - Status code: {e.response.status_code}")
        if e.response.status_code == 403: # Forbidden
             return {"error": f"Access to {url} is forbidden (403). This might be due to bot detection or regional restrictions."}
        elif e.response.status_code == 404: # Not Found
             return {"error": f"Product not found at {url} (404)."}
        elif e.response.status_code == 503: # Service Unavailable
             logging.warning(f"Service unavailable for {url} (503). This could be a temporary Amazon issue or a CAPTCHA page.")
             # Potentially trigger CAPTCHA logic here too if not already caught
             if "captcha" in e.response.text.lower():
                 # Simplified re-check, ideally CAPTCHA logic is more integrated
                 return {"error": "Service unavailable (503), possibly a CAPTCHA page. Manual CAPTCHA handling might be needed."}
             return {"error": "Service unavailable (503). Amazon might be temporarily down or blocking requests."}
        return {"error": f"HTTP error: {e}"}
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"error": f"Request failed: {e}"}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == '__main__':
    # Example usage:
    # Replace with a real Amazon product URL and your Anti-CAPTCHA API key (if needed for testing)
    # test_url = "https://www.amazon.com/Sample-Product-Example/dp/B0XXXXXXXX" # Replace with a valid URL
    # api_key = "YOUR_ANTI_CAPTCHA_API_KEY"  # Replace with your actual API key if testing CAPTCHA

    # print(f"Scraping product info from: {test_url}")

    # product_info = scrape_product_info(test_url) # Test without API key first
    # if product_info and 'error' not in product_info:
    #     print("Product Information:")
    #     for key, value in product_info.items():
    #         print(f"  {key.replace('_', ' ').title()}: {value}")
    # elif product_info and 'error' in product_info:
    #     print(f"Error: {product_info['error']}")
    #     # If CAPTCHA was the error, you might want to retry with an API key
    #     # if "CAPTCHA" in product_info['error'] and api_key != "YOUR_ANTI_CAPTCHA_API_KEY":
    #     #     print("\nRetrying with CAPTCHA API key...")
    #     #     product_info_with_captcha = scrape_product_info(test_url, captcha_api_key=api_key)
    #     #     if product_info_with_captcha and 'error' not in product_info_with_captcha:
    #     #         print("Product Information (after CAPTCHA attempt):")
    #     #         for key, value in product_info_with_captcha.items():
    #     #             print(f"  {key.replace('_', ' ').title()}: {value}")
    #     #     else:
    #     #         print(f"Error even with CAPTCHA key: {product_info_with_captcha.get('error', 'Unknown error')}")
    # else:
    #     print("Failed to retrieve product information for an unknown reason.")
    pass
