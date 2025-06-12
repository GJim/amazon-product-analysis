"""
Main entry point for the Amazon Product Analysis application.
This module sets up and runs the LangGraph workflow.
"""

import logging

# Import the workflow graph
from langchain_app.workflow.graph import create_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_analysis(amazon_url: str, max_products: int = 10, max_competitive: int = 5):
    """
    Run the product analysis workflow on a specific Amazon product URL.

    Args:
        amazon_url: URL of the Amazon product to analyze
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to analyze

    Returns:
        The final state of the workflow execution
    """
    # Create the workflow application
    app = create_workflow()

    # Prepare the initial input state
    initial_input = {
        "url": amazon_url,
        "main_product": None,
        "competitive_products": [],
        "messages": [f"Starting Amazon product analysis for {amazon_url}"],
        "error": None,
        # Pass the configuration parameters
        "max_products": max_products,
        "max_competitive": max_competitive,
    }

    logger.info(f"Starting analysis for URL: {amazon_url}")
    logger.info(
        f"Max products: {max_products}, Max competitive products: {max_competitive}"
    )

    # Run the workflow
    return app.invoke(initial_input)


def print_results(final_state):
    """Print the analysis results in a readable format."""
    print("\n" + "=" * 80)
    print("AMAZON PRODUCT ANALYSIS RESULTS")
    print("=" * 80)

    for message in final_state["messages"]:
        print(message)

    print("\n" + "=" * 80)
