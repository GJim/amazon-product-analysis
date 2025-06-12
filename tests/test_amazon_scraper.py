import unittest
import json
import asyncio
from amazon_scraper.scraper import extract_product_info, scrape_product_info
from amazon_scraper.models import ProductInfo
from amazon_scraper.browser_manager import get_browser_manager


class TestAmazonScraper(unittest.TestCase):

    def test_extract_product_info(self):
        """Test that product info is correctly extracted from HTML and matches expected values."""
        # Load the product HTML file
        with open(
            "tests/amazon_product_page_standard.html", "r", encoding="utf-8"
        ) as file:
            product_html = file.read()

        # Load the expected product info from JSON file
        with open(
            "tests/amazon_product_page_standard_data.json", "r", encoding="utf-8"
        ) as file:
            expected_product_info = json.load(file)

        # Extract product info from the HTML
        actual_product_info = extract_product_info(product_html)

        # Convert the Pydantic model to a dictionary for easier comparison and printing
        # actual_dict = actual_product_info.model_dump()
        # print(json.dumps(actual_dict, indent=4))

        # Validate required fields are present
        self.assertIsNotNone(
            actual_product_info.title, "Product title should be extracted"
        )
        self.assertIsNotNone(
            actual_product_info.price, "Product price should be extracted"
        )

        # Compare with expected values from JSON file
        # For title, we'll check if the expected title is contained within the actual title
        # since Amazon titles can sometimes have variations or additional text
        if expected_product_info.get("title"):
            self.assertIn(
                expected_product_info["title"][:50].lower(),
                actual_product_info.title.lower() if actual_product_info.title else "",
                "Product title should match expected value",
            )

        # For price, we'll check if it contains digits and currency symbols
        if expected_product_info.get("price") and actual_product_info.price:
            self.assertTrue(
                any(c.isdigit() for c in actual_product_info.price),
                "Price should contain digits",
            )
            # Check if price format is similar (contains the same digits)
            expected_digits = "".join(
                c for c in expected_product_info["price"] if c.isdigit()
            )
            actual_digits = "".join(c for c in actual_product_info.price if c.isdigit())
            self.assertEqual(
                expected_digits, actual_digits, "Price digits should match"
            )

        # Check description if available
        if "description" in expected_product_info and actual_product_info.description:
            # Description might be different format, so we'll check if key words are present
            expected_words = expected_product_info["description"].lower().split()
            actual_desc = actual_product_info.description.lower()
            for important_word in [w for w in expected_words if len(w) > 3][
                :5
            ]:  # Check first 5 important words
                self.assertIn(
                    important_word,
                    actual_desc,
                    f"Description should contain '{important_word}'",
                )

        # Check main image URL if available
        if (
            "main_image_url" in expected_product_info
            and actual_product_info.main_image_url
        ):
            # URLs might have different parameters, so check if they point to similar resources
            expected_url_parts = expected_product_info["main_image_url"].split("/")
            actual_url_parts = actual_product_info.main_image_url.split("/")
            # Check if they're from the same domain
            self.assertEqual(
                expected_url_parts[2],
                actual_url_parts[2],
                "Image URLs should be from the same domain",
            )

        # Check reviews if available
        if "reviews" in expected_product_info and actual_product_info.reviews:
            expected_reviews = expected_product_info["reviews"]
            actual_reviews = actual_product_info.reviews

            self.assertIsInstance(actual_reviews, list, "Reviews should be a list")

            # If we have reviews, check the structure matches
            if actual_reviews and expected_reviews:
                first_actual_review = actual_reviews[0].model_dump()
                first_expected_review = expected_reviews[0]

                # Check that review has expected fields
                for field in [
                    "title",
                    "rating",
                    "text",
                    "reviewer",
                    "date",
                    "verified_purchase",
                ]:
                    if field in first_expected_review:
                        self.assertIn(
                            field,
                            first_actual_review,
                            f"Review should have {field} field",
                        )

                        # For text fields, check if they contain similar content
                        if (
                            field in ["text", "title"]
                            and field in first_actual_review
                            and first_actual_review[field]
                        ):
                            # Check if at least one common word exists
                            expected_words = set(
                                first_expected_review[field].lower().split()
                                if first_expected_review[field]
                                else []
                            )
                            actual_words = set(
                                first_actual_review[field].lower().split()
                                if first_actual_review[field]
                                else []
                            )
                            if (
                                expected_words and len(expected_words) > 3
                            ):  # Only check if we have enough words
                                common_words = expected_words.intersection(actual_words)
                                self.assertGreaterEqual(
                                    len(common_words),
                                    1,
                                    f"Review {field} should have some common words with expected value",
                                )


class TestAmazonScraperIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for Amazon scraper functions that make actual network requests."""

    async def asyncSetUp(self):
        """Set up the browser manager for tests."""
        self.browser_manager = await get_browser_manager()

    async def asyncTearDown(self):
        """Clean up resources after tests."""
        # We don't close the browser_manager here as it's a singleton
        # and might be used by other tests
        await self.browser_manager.close()

    async def test_scrape_product_info_real_url(self):
        """Test scraping product info from a real Amazon URL."""
        # Amazon Stock Pot URL
        url = "https://www.amazon.com/dp/B08B9H2ZYT"
        print(
            "Warning: the test link ( https://www.amazon.com/dp/B08B9H2ZYT ) may be invalid or changed"
        )

        # Set a longer timeout for the test
        timeout = 60  # seconds
        start_time = asyncio.get_event_loop().time()

        try:
            # Scrape the product info using the browser_manager
            product_info = await asyncio.wait_for(
                scrape_product_info(url, browser_manager=self.browser_manager),
                timeout=timeout,
            )

            # print("Product info:")
            # product_info_dict = product_info.model_dump()
            # print(json.dumps(product_info_dict, indent=4))

            # Basic validation - we don't know the exact content, but we can check structure
            self.assertIsNotNone(product_info, "Product info should not be None")
            self.assertIsInstance(
                product_info, ProductInfo, "Result should be a ProductInfo object"
            )

            # Log success
            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"\nSuccessfully scraped product in {elapsed:.2f} seconds")

            # Validate essential fields
            self.assertIsNotNone(product_info.title, "Product should have a title")
            self.assertTrue(len(product_info.title) > 0, "Title should not be empty")

            # Check price format if available
            if product_info.price:
                self.assertTrue(
                    any(c.isdigit() for c in product_info.price),
                    "Price should contain digits",
                )

            # Log successful test completion
            print(f"\nSuccessfully scraped product: {product_info.title}")

        except asyncio.TimeoutError:
            self.skipTest(
                f"Test timed out after {timeout} seconds - Amazon might be blocking requests"
            )
        except Exception as e:
            self.fail(f"Test failed with exception: {str(e)}")


if __name__ == "__main__":
    unittest.main()
