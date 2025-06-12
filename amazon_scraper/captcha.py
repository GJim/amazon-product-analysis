"""
Functions for detecting and handling CAPTCHA challenges on Amazon pages.
"""

from bs4 import BeautifulSoup


def is_recaptcha_page(html: str) -> bool:
    """
    Check if the page contains a CAPTCHA challenge.

    Args:
        html: HTML content of the page.

    Returns:
        bool: True if CAPTCHA is detected, False otherwise.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Check if the page contains the word "recaptcha" (case-insensitive)
    has_recaptcha = "recaptcha" in html.lower()

    # Check if the page contains a div with id "captchacharacters"
    has_captchacharacters = soup.find("div", {"id": "captchacharacters"}) is not None

    # Check if the page contains the word "captcha" (case-insensitive)
    has_captcha = "captcha" in html.lower()

    # If any of the above conditions are true, return True
    return has_recaptcha or has_captchacharacters or has_captcha
