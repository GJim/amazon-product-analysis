"""Workflow nodes for the Amazon product analysis app."""

import logging
import asyncio

from langchain_app.workflow.state import GraphState
from langchain_app.core.collector import ProductCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_collector(state: GraphState) -> GraphState:
    """
    Initialize the product collector.
    """
    logger.info("Initializing product collector")
    
    # Get configuration parameters from state, with defaults if not provided
    max_products = state.get("max_products", 10)
    max_competitive = state.get("max_competitive", 5)
    min_competitive = min(3, max_competitive)  # Default to 3 or max_competitive if less
    
    # Create collector with configuration
    collector = ProductCollector()
    collector.max_products = max_products
    collector.max_competitive_products = max_competitive
    collector.min_competitive_products = min_competitive
    
    state["collector"] = collector
    state["messages"].append(f"Product collector initialized (max products: {max_products}, max competitive: {max_competitive})")
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

    # We use the synchronous wrapper to run the async method
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        state["competitive_products"] = loop.run_until_complete(
            collector.collect_competitive_products_async(main_product)
        )
    except Exception as e:
        state["error"] = f"Error collecting competitive products: {str(e)}"
        state["messages"].append(state["error"])
        return state

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
