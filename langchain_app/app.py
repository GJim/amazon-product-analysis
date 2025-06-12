from typing import TypedDict, Annotated, List, Dict, Any, Optional, Set
import operator
import time
import logging
import re
import asyncio
from queue import Queue, Empty
from dataclasses import dataclass, field
from datetime import datetime

from langgraph.graph import StateGraph, END
import sys
import os

# Add the parent directory to sys.path to import amazon_scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from amazon_scraper.scraper import scrape_product_info
from amazon_scraper.browser_manager import get_browser_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Class to store product information with metadata."""

    url: str
    data: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)
    is_main_product: bool = False
    similarity_score: float = 0.0

    @property
    def title(self) -> str:
        """Get the product title."""
        return self.data.get("title", "Unknown Title")

    @property
    def price(self) -> str:
        """Get the product price."""
        return self.data.get("price", "Unknown Price")

    @property
    def asin(self) -> str:
        """Get the product ASIN."""
        # Check if ASIN is in details
        if "details" in self.data and self.data["details"]:
            details = self.data["details"]
            if isinstance(details, dict) and "asin" in details:
                return details["asin"]
        return self.data.get("asin", "")

    @property
    def description(self) -> str:
        """Get the product description."""
        return self.data.get("description", "")

    @property
    def similar_items_links(self) -> List[str]:
        """Get the similar items links."""
        return self.data.get("similar_items_links", [])

    def __str__(self) -> str:
        """String representation of the product."""
        return f"Product(title={self.title}, price={self.price}, asin={self.asin})"


class ProductCollector:
    """Class to manage product collection with synchronization."""

    def __init__(self):
        """Initialize the product collector."""
        self.collected_products: Dict[str, Product] = {}  # Store by URL
        self.collected_asins: Set[str] = set()  # Track collected ASINs
        self.url_queue = Queue()  # Queue for URLs to process
        self.max_products = 10  # Maximum number of products to collect
        self.min_competitive_products = 3  # Minimum number of competitive products
        self.max_competitive_products = 5  # Maximum number of competitive products

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

    def collect_product(
        self, url: str, is_main_product: bool = False
    ) -> Optional[Product]:
        """
        Collect product information from a URL with synchronization.

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
        product_data = None

        # Create a new event loop for this operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:

            async def _scrape_with_browser():
                # Get a new browser manager instance
                logger.info("Getting browser manager for product collection")
                browser_manager = await get_browser_manager()

                try:
                    # Scrape product info with timeout using the browser manager
                    return await asyncio.wait_for(
                        scrape_product_info(url, browser_manager=browser_manager),
                        timeout=60.0,
                    )
                finally:
                    # Close the browser manager after use
                    logger.info("Closing browser manager after product collection")
                    await browser_manager.close()

            # Run the scraping function
            product_data = loop.run_until_complete(_scrape_with_browser())

        except asyncio.TimeoutError:
            logger.error(f"Timeout while scraping product from URL: {url}")
            return None
        except Exception as e:
            logger.error(f"Error during product scraping: {str(e)}")
            return None
        finally:
            # Clean up any remaining tasks
            try:
                # Cancel all running tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()

                # Give tasks a chance to terminate
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )

                # Shutdown async generators
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception as e:
                logger.error(f"Error during event loop cleanup: {str(e)}")
            finally:
                # Close the loop
                loop.close()

        if not product_data:
            logger.warning(f"Failed to collect product from URL: {url}")
            return None

        # Create product object
        product = Product(
            url=url, data=product_data.model_dump(), is_main_product=is_main_product
        )

        # Store product
        self.collected_products[url] = product
        if asin:
            self.collected_asins.add(asin)
        elif product.asin:
            self.collected_asins.add(product.asin)

        logger.info(f"Successfully collected product: {product.title}")
        return product

    def cleanup(self):
        """Clean up resources used by the collector."""
        logger.info("Cleaning up product collector resources")
        # No browser manager to clean up as we create and close it for each operation
        # Just log that cleanup was called
        logger.info("Product collector cleanup completed")

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
        if (
            main_product.data.get("manufacturer", "").lower()
            != comp_product.data.get("manufacturer", "").lower()
        ):
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
        main_desc = main_product.description.lower()
        comp_desc = comp_product.description.lower()

        # Simple feature comparison - look for keywords in one description but not the other
        distinguishing_keywords = [
            "wireless",
            "bluetooth",
            "waterproof",
            "rechargeable",
            "portable",
            "professional",
            "premium",
            "budget",
        ]

        for keyword in distinguishing_keywords:
            if (keyword in main_desc and keyword not in comp_desc) or (
                keyword not in main_desc and keyword in comp_desc
            ):
                score += 0.05  # Small boost for each distinguishing feature

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
        competitive_products = []

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


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        url: The initial Amazon product URL
        collector: The ProductCollector instance
        main_product: The main product being analyzed
        competitive_products: List of competitive products
        messages: List of messages for tracking progress
        error: Any error message
    """

    url: str
    collector: ProductCollector
    main_product: Optional[Product]
    competitive_products: List[Product]
    messages: Annotated[list, operator.add]
    error: Optional[str]


def initialize_collector(state: GraphState) -> GraphState:
    """
    Initialize the product collector.
    """
    logger.info("Initializing product collector")
    state["collector"] = ProductCollector()
    state["messages"].append("Product collector initialized")
    state["competitive_products"] = []
    return state


def scrape_main_product(state: GraphState) -> GraphState:
    """
    Scrape the main product information.
    """
    url = state["url"]
    collector = state["collector"]

    logger.info(f"Scraping main product from URL: {url}")
    state["messages"].append(f"Scraping main product from URL: {url}")

    # Validate URL
    if not collector.is_valid_amazon_url(url):
        state["error"] = f"Invalid Amazon URL: {url}"
        state["messages"].append(state["error"])
        return state

    # Collect main product
    main_product = collector.collect_product(url, is_main_product=True)

    if not main_product:
        state["error"] = f"Failed to collect main product from URL: {url}"
        state["messages"].append(state["error"])
        return state

    state["main_product"] = main_product
    state["messages"].append(
        f"Successfully collected main product: {main_product.title}"
    )

    # Add similar items to queue
    for similar_url in main_product.similar_items_links:
        collector.url_queue.put(similar_url)

    state["messages"].append(
        f"Added {len(main_product.similar_items_links)} competitive product URLs to queue"
    )
    return state


def collect_competitive_products(state: GraphState) -> GraphState:
    """
    Collect information about competitive products.
    """
    collector = state["collector"]
    main_product = state["main_product"]

    if not main_product:
        state["error"] = "Main product not available"
        state["messages"].append(state["error"])
        return state

    logger.info("Collecting competitive products")
    state["messages"].append("Collecting competitive products")

    # Process URLs from the queue until we have enough products or the queue is empty
    collected_count = 0
    max_attempts = 20  # Limit attempts to prevent infinite loops
    attempts = 0

    while (
        collected_count < collector.max_competitive_products
        and attempts < max_attempts
        and not collector.url_queue.empty()
        and len(collector.collected_products) < collector.max_products
    ):

        try:
            url = collector.url_queue.get(block=False)
            attempts += 1

            # Skip if we've already collected this product
            asin = collector.extract_asin_from_url(url)
            if asin and asin in collector.collected_asins:
                continue

            # Collect product
            product = collector.collect_product(url)
            if product:
                collected_count += 1
                state["messages"].append(
                    f"Collected competitive product {collected_count}: {product.title}"
                )

                # Add more similar items to queue if needed
                if (
                    collected_count < collector.min_competitive_products
                    and len(product.similar_items_links) > 0
                ):
                    for similar_url in product.similar_items_links[
                        :3
                    ]:  # Limit to 3 per product
                        collector.url_queue.put(similar_url)

            # Add a small delay to prevent rate limiting
            time.sleep(1)

        except Empty:
            break

    # Select the most distinguishing competitive products
    state["competitive_products"] = collector.select_competitive_products(main_product)

    state["messages"].append(
        f"Selected {len(state['competitive_products'])} most distinguishing competitive products"
    )
    return state


def analyze_products(state: GraphState) -> GraphState:
    """
    Analyze the main product and its competitors.
    """
    main_product = state["main_product"]
    competitive_products = state["competitive_products"]
    collector = state["collector"]

    if not main_product:
        state["error"] = "Main product not available for analysis"
        state["messages"].append(state["error"])
        return state

    logger.info("Analyzing products")
    state["messages"].append("Analyzing products")

    # Generate analysis summary
    analysis = [
        f"# Product Analysis Report",
        f"\n## Main Product: {main_product.title}",
        f"- Price: {main_product.price}",
        f"- ASIN: {main_product.asin}",
    ]

    if main_product.description:
        analysis.append(f"- Description: {main_product.description[:200]}...")

    if competitive_products:
        analysis.append(f"\n## Competitive Products ({len(competitive_products)})")

        for i, product in enumerate(competitive_products, 1):
            analysis.append(f"\n### {i}. {product.title}")
            analysis.append(f"- Price: {product.price}")
            analysis.append(f"- ASIN: {product.asin}")
            analysis.append(f"- Distinguishing Score: {product.similarity_score:.2f}")

            if product.description:
                analysis.append(f"- Description: {product.description[:150]}...")
    else:
        analysis.append("\n## No competitive products found")

    state["messages"].append("\n".join(analysis))

    # Clean up resources when done
    if collector:
        collector.cleanup()

    return state


def route_based_on_error(state: GraphState):
    """
    Determine the next node based on whether there's an error.
    """
    if state.get("error"):
        return "handle_error"
    return "analyze_products"


def handle_error(state: GraphState) -> GraphState:
    """
    Handle any errors that occurred during processing.
    """
    error = state.get("error", "Unknown error")
    logger.error(f"Error in workflow: {error}")
    state["messages"].append(f"Error occurred: {error}")

    # Clean up resources
    if "collector" in state and state["collector"]:
        state["collector"].cleanup()

    return state


# Instantiate the graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("initialize_collector", initialize_collector)
workflow.add_node("scrape_main_product", scrape_main_product)
workflow.add_node("collect_competitive_products", collect_competitive_products)
workflow.add_node("analyze_products", analyze_products)
workflow.add_node("handle_error", handle_error)

# Set the entry point
workflow.set_entry_point("initialize_collector")

# Add edges
workflow.add_edge("initialize_collector", "scrape_main_product")
workflow.add_edge("scrape_main_product", "collect_competitive_products")
workflow.add_conditional_edges(
    "collect_competitive_products",
    route_based_on_error,
    "analyze_products",
    "handle_error",
)
workflow.add_edge("analyze_products", END)
workflow.add_edge("handle_error", END)

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    # Example Amazon product URL
    amazon_url = "https://www.amazon.com/dp/B08B9H2ZYT"  # Example URL - replace with actual product

    initial_input = {
        "url": amazon_url,
        "main_product": None,
        "competitive_products": [],
        "messages": ["Starting Amazon product analysis"],
        "error": None,
    }

    print(f"Starting analysis for URL: {amazon_url}")
    final_state = app.invoke(initial_input)

    print("\nAnalysis Results:")
    for message in final_state["messages"]:
        print(message)
