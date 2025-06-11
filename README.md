# Amazon Product Scraper

This Python library helps scrape product information from Amazon URLs. It includes functionality to handle reCAPTCHA challenges using an external CAPTCHA solving service (Anti-CAPTCHA).

## Features

- Fetch product title, price, description, and main image URL.
- Basic handling of reCAPTCHA via Anti-CAPTCHA service.
- Configurable logging for monitoring and debugging.

## Prerequisites

- Python 3.7+
- An API key from a CAPTCHA solving service like [Anti-CAPTCHA](https://anti-captcha.com/). This is only required if you anticipate encountering CAPTCHAs.

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd amazon-product-scraper
    ```
    *(Replace `<repository_url>` with the actual URL of this repository)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The primary function provided by this library is `scrape_product_info`.

```python
from amazon_scraper import scrape_product_info

# URL of the Amazon product page you want to scrape
amazon_url = "https://www.amazon.com/Example-Product/dp/B0XXXXXXXX" # Replace with a real Amazon product URL

# Your Anti-CAPTCHA API key (required if CAPTCHA is encountered)
# It's recommended to store API keys securely, e.g., in environment variables or a config file.
anti_captcha_api_key = "YOUR_ANTI_CAPTCHA_API_KEY" # Replace with your actual key or set to None

# Scrape the product information
# If you don't expect a CAPTCHA or don't have an API key, you can omit captcha_api_key:
# product_info = scrape_product_info(amazon_url)
product_info = scrape_product_info(amazon_url, captcha_api_key=anti_captcha_api_key)

if product_info:
    if 'error' in product_info:
        print(f"Error scraping product: {product_info['error']}")
    else:
        print("Product Information:")
        print(f"  Title: {product_info.get('title')}")
        print(f"  Price: {product_info.get('price')}")
        print(f"  Description: {product_info.get('description')}")
        print(f"  Image URL: {product_info.get('main_image_url')}")
        print(f"  Scraped URL: {product_info.get('url')}")
else:
    print("Failed to retrieve any information for the product.")

```

### Handling CAPTCHAs

- If the scraper encounters a page that it suspects is a CAPTCHA, it will attempt to use the `captcha_api_key` provided to `scrape_product_info` to solve it via the Anti-CAPTCHA service.
- The `amazon_scraper.utils.solve_recaptcha` function handles the interaction with the Anti-CAPTCHA API.
- **Important**: The current CAPTCHA handling is basic. It detects CAPTCHAs, solves them, and then attempts to parse the product information. However, Amazon's CAPTCHA implementation can be complex. Successfully solving a CAPTCHA token does not always guarantee that the subsequent request will bypass the protection, especially if the CAPTCHA is part of a form submission flow. The scraper currently logs a warning in such cases. Further enhancements might be needed for more robust CAPTCHA bypassing.

### Logging

The library uses the standard Python `logging` module. By default, it logs INFO level messages. You can configure this as needed in your application.

```python
import logging

# To see more detailed logs (e.g., for debugging the scraper)
logging.basicConfig(level=logging.DEBUG)

# Then use the scraper as usual
# from amazon_scraper import scrape_product_info
# ...
```

## LangChain Application

This project now includes a simple example demonstrating a LangGraph setup.
The application showcases a basic graph with a few nodes that append messages to a shared state.

For more details on this example and how to run it, please see the [LangChain Application README](./langchain_app/README.md).

## Development & Testing

### Running Tests
```bash
# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests/test_scraper.py

# Run with verbose output
python -m unittest discover -v tests
```

### Test Coverage
To generate a test coverage report:

```bash
pip install coverage
coverage run -m unittest discover tests
coverage report -m
coverage html  # Generates HTML report in htmlcov/
```

### Test Fixtures
The test suite includes HTML fixtures of Amazon product pages in the `tests/` directory. When adding new test cases, please include both the HTML file and an expected JSON output file following the naming convention:
- `amazon_product_page_*.html` - The HTML fixture
- `amazon_product_page_*_data.json` - Expected output data

## Disclaimer

- Web scraping Amazon's website may be against their Terms of Service. Use this library responsibly and at your own risk.
- Amazon's website structure can change frequently, which may break the scraper. The selectors used for finding product information may need to be updated over time.
- This library is for educational purposes.
