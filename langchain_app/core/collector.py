"""Product collector for the Amazon product analysis app."""

import asyncio
import logging
import re
from queue import Queue, Empty
from typing import Dict, Set, List, Optional

import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to import amazon_scraper
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from amazon_scraper.scraper import scrape_product_info
from amazon_scraper.browser_manager import get_browser_manager

from langchain_app.core.models import Product


class ProductCollector:
    """Class to manage product collection with optimized browser management."""

    def __init__(
        self,
        max_products: int = 10,
        max_competitive_products: int = 5,
        max_attempts: int = 20,
    ):
        """Initialize the product collector."""
        self.collected_products: Dict[str, Product] = {}  # Store by URL
        self.collected_asins: Set[str] = set()  # Track collected ASINs
        self.url_queue = Queue()  # Queue for URLs to process
        self.max_products = max_products  # Maximum number of products to collect
        self.max_competitive_products = (
            max_competitive_products  # Maximum number of competitive products
        )
        self.max_attempts = (
            max_attempts  # Maximum number of attempts to collect products
        )
        self._browser_manager = None  # Will be initialized when needed

    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL."""
        asin_patterns = [
            r"/dp/([A-Z0-9]{10})/?",
            r"/product/([A-Z0-9]{10})/?",
            r"/gp/product/([A-Z0-9]{10})/?",
        ]

        for pattern in asin_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def is_valid_amazon_url(self, url: str) -> bool:
        """Check if the URL is a valid Amazon product URL."""
        if not url.startswith(("http://", "https://")):
            return False

        if not re.search(r"amazon\.(com|co\.uk|de|fr|it|es|ca|jp|in)", url):
            return False

        # Check if it contains a product identifier
        if not re.search(r"/(dp|gp/product|product)/[A-Z0-9]{10}", url):
            return False

        return True

    async def _get_browser_manager(self):
        """Get a browser manager instance, reusing if possible."""
        if self._browser_manager is None:
            logger.info("Initializing new browser manager")
            self._browser_manager = await get_browser_manager()
        return self._browser_manager

    async def collect_product_async(
        self, url: str, is_main_product: bool = False
    ) -> Optional[Product]:
        """
        Collect product information asynchronously.

        Args:
            url: The Amazon product URL
            is_main_product: Whether this is the main product

        Returns:
            Product object if successful, None otherwise
        """
        # Validate URL
        if not self.is_valid_amazon_url(url):
            logger.warning(f"Invalid Amazon URL: {url}")
            return None

        # Check if we've already collected this product
        asin = self.extract_asin_from_url(url)
        if asin and asin in self.collected_asins:
            logger.info(f"Product with ASIN {asin} already collected")
            return self.collected_products.get(url)

        logger.info(f"Collecting product from URL: {url}")

        try:
            # Get browser manager
            browser_manager = await self._get_browser_manager()

            # Scrape product info with timeout
            product_data = await asyncio.wait_for(
                scrape_product_info(url, browser_manager=browser_manager), timeout=60.0
            )

            # convert all keys in product_data.details.specifications to lowercase
            if product_data:
                product_data.details.specifications = {
                    k.lower(): v for k, v in product_data.details.specifications.items()
                }

            if not product_data:
                logger.warning(f"Failed to collect product from URL: {url}")
                return None

            # Create product object
            product = Product(
                url=url, product_info=product_data, is_main_product=is_main_product
            )

            # Store product
            self.collected_products[url] = product
            if asin:
                self.collected_asins.add(asin)
            elif product.asin:
                self.collected_asins.add(product.asin)

            # Add similar items to queue
            if product.similar_items_links:
                for similar_url in product.similar_items_links[:3]:
                    self.url_queue.put(similar_url)

            logger.info(f"Successfully collected product: {product.title}")
            return product

        except asyncio.TimeoutError:
            logger.error(f"Timeout while scraping product from URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Error during product scraping: {str(e)}")
            return None

    def collect_product(
        self, url: str, is_main_product: bool = False
    ) -> Optional[Product]:
        """
        Collect product information from a URL.

        This is a synchronous wrapper around the async method.

        Args:
            url: The Amazon product URL
            is_main_product: Whether this is the main product

        Returns:
            Product object if successful, None otherwise
        """
        # Create or get the event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(
                self.collect_product_async(url, is_main_product)
            )
        except Exception as e:
            logger.error(f"Error during product collection: {str(e)}")
            return None

    async def cleanup_async(self):
        """Clean up resources used by the collector asynchronously."""
        logger.info("Cleaning up product collector resources")
        if self._browser_manager:
            try:
                await self._browser_manager.close()
                self._browser_manager = None
                logger.info("Browser manager closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser manager: {str(e)}")

    def cleanup(self):
        """Clean up resources used by the collector synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.cleanup_async())
        except Exception as e:
            logger.error(f"Error during collector cleanup: {str(e)}")

    def calculate_similarity_score(
        self, main_product: Product, comp_product: Product
    ) -> float:
        """
        Calculate similarity score between main product and competitive product.
        Higher score means more distinguishing (different) from main product.

        Args:
            main_product: The main product
            comp_product: The competitive product

        Returns:
            Similarity score (0-1, higher means more distinguishing)
        """
        score = 0.0

        # Different manufacturer/brand is distinguishing
        main_manufacturer = ""
        comp_manufacturer = ""

        # Try to get manufacturer from details
        if (
            main_product.product_info.details
            and "manufacturer" in main_product.product_info.details.specifications
        ):
            main_manufacturer = main_product.product_info.details.specifications[
                "manufacturer"
            ]

        if (
            comp_product.product_info.details
            and "manufacturer" in comp_product.product_info.details.specifications
        ):
            comp_manufacturer = comp_product.product_info.details.specifications[
                "manufacturer"
            ]

        if main_manufacturer.lower() != comp_manufacturer.lower():
            score += 0.3

        # Price difference is distinguishing
        try:
            main_price = float(re.sub(r"[^\d.]", "", main_product.price))
            comp_price = float(re.sub(r"[^\d.]", "", comp_product.price))
            price_diff = abs(main_price - comp_price) / max(main_price, comp_price)
            score += min(0.3, price_diff)  # Cap at 0.3
        except (ValueError, ZeroDivisionError):
            # If we can't parse prices, assume some difference
            score += 0.1

        # Different features are distinguishing
        main_words = (
            set(main_product.description.lower().split())
            if main_product.description
            else set()
        )
        comp_words = (
            set(comp_product.description.lower().split())
            if comp_product.description
            else set()
        )

        differing_words = main_words.symmetric_difference(comp_words)
        score += min(
            0.3, len(differing_words) / max(len(main_words), len(comp_words))
        )  # Cap at 0.3

        # Different product categories are distinguishing
        main_categories = set(main_product.product_info.details.categories)
        comp_categories = set(comp_product.product_info.details.categories)
        differing_categories = main_categories.symmetric_difference(comp_categories)
        score += min(
            0.2,
            len(differing_categories) / max(len(main_categories), len(comp_categories)),
        )  # Cap at 0.2

        # Cap the score at 1.0
        return min(1.0, score)

    def select_competitive_products(self, main_product: Product) -> List[Product]:
        """
        Select the most distinguishing competitive products.

        Args:
            main_product: The main product

        Returns:
            List of selected competitive products
        """
        # Get all products except the main one
        candidates = [
            p for p in self.collected_products.values() if not p.is_main_product
        ]

        # Calculate similarity scores
        for product in candidates:
            product.similarity_score = self.calculate_similarity_score(
                main_product, product
            )

        # Sort by similarity score (higher score = more distinguishing)
        candidates.sort(key=lambda p: p.similarity_score, reverse=True)

        # Select top products (between min and max competitive products)
        return candidates[: self.max_competitive_products]

    async def collect_competitive_products_async(
        self, main_product: Product
    ) -> List[Product]:
        """
        Collect and select competitive products asynchronously.

        Args:
            main_product: The main product

        Returns:
            List of competitive products
        """
        if not main_product:
            logger.error("Main product not available")
            return []

        logger.info("Collecting competitive products")

        # Process URLs from the queue
        collected_count = 0
        attempts = 0

        while (
            collected_count < self.max_competitive_products
            and attempts < self.max_attempts
            and not self.url_queue.empty()
            and len(self.collected_products) < self.max_products
        ):
            try:
                url = self.url_queue.get(block=False)
                attempts += 1

                # Skip if we've already collected this product
                asin = self.extract_asin_from_url(url)
                if asin and asin in self.collected_asins:
                    continue

                # Collect product asynchronously
                product = await self.collect_product_async(url)
                if product:
                    collected_count += 1

                # Add a small delay to prevent rate limiting
                await asyncio.sleep(1)

            except Empty:
                break

        # Select the most distinguishing competitive products
        return self.select_competitive_products(main_product)
