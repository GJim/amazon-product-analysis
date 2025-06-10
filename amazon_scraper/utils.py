from anticaptchaofficial.recaptchav2proxyless import *

def solve_recaptcha(site_key: str, page_url: str, api_key: str) -> str | None:
    """
    Solves a reCAPTCHA v2 challenge using the Anti-CAPTCHA service.

    Args:
        site_key: The reCAPTCHA site key found on the page.
        page_url: The URL of the page with the reCAPTCHA.
        api_key: Your Anti-CAPTCHA API key.

    Returns:
        The reCAPTCHA solution token if successful, None otherwise.
    """
    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)  # Optional: for detailed logging
    solver.set_key(api_key)
    solver.set_website_url(page_url)
    solver.set_website_key(site_key)

    # Optional: Set soft_id for your software (see Anti-CAPTCHA documentation)
    # solver.set_soft_id(0)

    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        print(f"Successfully solved reCAPTCHA. Solution: {g_response}")
        return g_response
    else:
        print(f"Error solving reCAPTCHA: {solver.error_code} - {solver.error_description}")
        return None

if __name__ == '__main__':
    # This is an example of how to use the function.
    # Replace with a real site key, page URL, and your API key for testing.
    # IMPORTANT: Do not commit your actual API key to version control.
    # Consider using environment variables or a configuration file for API keys.

    # example_site_key = "your_site_key_here"  # Replace with a real site key
    # example_page_url = "your_page_url_here"  # Replace with a real page URL
    # example_api_key = "YOUR_ANTI_CAPTCHA_API_KEY" # Replace with your actual API key

    # print("Attempting to solve reCAPTCHA (example)...")
    # solution = solve_recaptcha(example_site_key, example_page_url, example_api_key)
    # if solution:
    #     print(f"Example reCAPTCHA solution: {solution}")
    # else:
    #     print("Failed to solve example reCAPTCHA.")
    pass
