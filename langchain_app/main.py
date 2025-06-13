"""
Main entry point for the Amazon Product Analysis application.
This module sets up and runs the multi-agent LangGraph workflow.
"""

import logging
import asyncio
import datetime
import dotenv

dotenv.load_dotenv()

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
    """Print the analysis results in a well-formatted report."""
    # Get data from state
    main_product = final_state.get("main_product")
    competitive_products = final_state.get("competitive_products", [])
    market_analysis = final_state.get("market_analysis", {})
    optimization_suggestions = final_state.get("optimization_suggestions", {})
    messages = final_state.get("messages", [])

    # Define report sections and formatting
    border = "=" * 80
    section_border = "-" * 80
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print report header
    print(f"\n{border}")
    print(f"AMAZON PRODUCT ANALYSIS REPORT - {timestamp}")
    print(f"{border}\n")

    # 1. Main Product Information
    if main_product:
        print("📦 MAIN PRODUCT INFORMATION")
        print(section_border)
        print(f"Title: {main_product.title}")
        print(
            f"Price: ${main_product.price if hasattr(main_product, 'price') else 'N/A'}"
        )
        print(
            f"Rating: {main_product.rating if hasattr(main_product, 'rating') else 'N/A'} ⭐ ({main_product.review_count if hasattr(main_product, 'review_count') else 'N/A'} reviews)"
        )
        print(f"URL: {main_product.url if hasattr(main_product, 'url') else 'N/A'}")

        if hasattr(main_product, "features") and main_product.features:
            print("\nKey Features:")
            for i, feature in enumerate(main_product.features[:5], 1):
                print(f"  {i}. {feature}")
        print("\n")

    # 2. Market Analysis
    print("📊 MARKET ANALYSIS")
    print(section_border)

    if isinstance(market_analysis, dict):
        # Market position
        if "market_position" in market_analysis:
            print(f"Market Position: {market_analysis['market_position']}")

        # Competitive advantages
        if (
            "competitive_advantages" in market_analysis
            and market_analysis["competitive_advantages"]
        ):
            print("\nCompetitive Advantages:")
            for i, adv in enumerate(market_analysis["competitive_advantages"], 1):
                print(f"  ✓ {adv}")

        # Competitive disadvantages
        if (
            "competitive_disadvantages" in market_analysis
            and market_analysis["competitive_disadvantages"]
        ):
            print("\nCompetitive Disadvantages:")
            for i, disadv in enumerate(market_analysis["competitive_disadvantages"], 1):
                print(f"  ✗ {disadv}")

        # Price positioning
        if (
            "price_positioning" in market_analysis
            and market_analysis["price_positioning"]
        ):
            print("\nPrice Positioning:")
            price_data = market_analysis["price_positioning"]
            if isinstance(price_data, dict):
                for key, value in price_data.items():
                    print(f"  • {key}: {value}")
            else:
                print(f"  • {price_data}")
    elif isinstance(market_analysis, str):
        print(market_analysis)
    elif isinstance(market_analysis, list):
        for item in market_analysis:
            print(item)
            print()
    else:
        print("No detailed market analysis available.")
    print("\n")

    # 3. Competitive Products Summary
    print("🔍 COMPETITIVE PRODUCTS SUMMARY")
    print(section_border)
    print(f"Number of competitive products analyzed: {len(competitive_products)}")

    if competitive_products:
        print("\nTop Competitors:")
        for i, product in enumerate(competitive_products[:3], 1):
            print(
                f"  {i}. {product.title if hasattr(product, 'title') else 'Unnamed Product'}"
            )
            print(
                f"     Price: ${product.price if hasattr(product, 'price') else 'N/A'}"
            )
            print(
                f"     Rating: {product.rating if hasattr(product, 'rating') else 'N/A'} ⭐"
            )
    print("\n")

    # 4. Optimization Suggestions
    print("💡 OPTIMIZATION SUGGESTIONS")
    print(section_border)

    if optimization_suggestions:
        print(optimization_suggestions)
    else:
        print("No optimization suggestions available.")
    print("\n")

    # 5. Report Summary
    print("📝 REPORT SUMMARY")
    print(section_border)
    print(f"Analysis completed at: {timestamp}")
    print(
        f"Products analyzed: {len(competitive_products) + 1} (1 main + {len(competitive_products)} competitive)"
    )

    # Find the final summary message if available
    summary_message = ""
    for message in reversed(messages):
        if "summary" in message.lower() and len(message) > 50:
            summary_message = message
            break

    if summary_message:
        print("\nExecutive Summary:")
        print(f"{summary_message}")

    print(f"\n{border}")
    print("End of Report")
    print(f"{border}")

    # Return a success message
    return "Report generated successfully."
