"""
Main entry point for the Amazon Product Analysis application.
This module sets up and runs the multi-agent LangGraph workflow.
"""

import logging
import asyncio

# Import the multi-agent workflow graph
from langchain_app.workflow.multi_agent_graph import run_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_analysis(amazon_url: str, max_products: int = 10, max_competitive: int = 5):
    """
    Run the multi-agent product analysis workflow on a specific Amazon product URL.

    Args:
        amazon_url: URL of the Amazon product to analyze
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to analyze

    Returns:
        The final state of the workflow execution
    """
    # Prepare the initial input state
    initial_input = {
        "url": amazon_url,
        "main_product": None,
        "competitive_products": [],
        "market_analysis": None,
        "optimization_suggestions": [],
        "messages": [f"Starting Amazon product analysis for {amazon_url}"],
        "error": None,
        # Pass the configuration parameters
        "max_products": max_products,
        "max_competitive": max_competitive,
        # Multi-agent specific fields
        "current_agent": "supervisor",
        "task_complete": False,
    }

    logger.info(f"Starting multi-agent analysis for URL: {amazon_url}")
    logger.info(
        f"Max products: {max_products}, Max competitive products: {max_competitive}"
    )

    # Run the workflow using the synchronous wrapper
    return run_workflow(initial_input)


async def run_analysis_async(
    amazon_url: str, max_products: int = 10, max_competitive: int = 5
):
    """
    Run the multi-agent product analysis workflow asynchronously.

    Args:
        amazon_url: URL of the Amazon product to analyze
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to analyze

    Returns:
        The final state of the workflow execution
    """
    from langchain_app.workflow.multi_agent_graph import run_workflow_async

    # Prepare the initial input state
    initial_input = {
        "url": amazon_url,
        "main_product": None,
        "competitive_products": [],
        "market_analysis": None,
        "optimization_suggestions": [],
        "messages": [f"Starting Amazon product analysis for {amazon_url}"],
        "error": None,
        # Pass the configuration parameters
        "max_products": max_products,
        "max_competitive": max_competitive,
        # Multi-agent specific fields
        "current_agent": "supervisor",
        "task_complete": False,
    }

    logger.info(f"Starting async multi-agent analysis for URL: {amazon_url}")
    return await run_workflow_async(initial_input)


def print_results(final_state):
    """Print the analysis results in a readable format."""
    print("\n" + "=" * 80)
    print("MULTI-AGENT AMAZON PRODUCT ANALYSIS RESULTS")
    print("=" * 80)

    for message in final_state["market_analysis"]:
        print(message)

    print("\n" + "=" * 80)

    # Print additional information about the multi-agent workflow
    print(
        f"Analysis completed with {len(final_state.get('competitive_products', []))} competitive products"
    )
    print(f"Market analysis: {final_state.get('market_analysis') is not None}")
    print(
        f"Optimization suggestions: {len(final_state.get('optimization_suggestions', {})) > 0}"
    )
    print("=" * 80)
