"""
Main entry point for the Amazon Product Analysis application.
This module sets up and runs the multi-agent LangGraph workflow.
"""

import logging
import datetime
import dotenv
from langchain_app.workflow.state import GraphState, create_graph_state

dotenv.load_dotenv()

# Import the multi-agent workflow graph
from langchain_app.workflow.multi_agent_graph import run_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_analysis(
    amazon_url: str,
    task_id: str,
    max_products: int = 10,
    max_competitive: int = 5,
):
    """
    Run the multi-agent product analysis workflow on a specific Amazon product URL.

    Args:
        amazon_url: URL of the Amazon product to analyze
        task_id: Task ID for existing task
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to analyze

    Returns:
        The final state of the workflow execution
    """
    # Prepare the initial input state
    initial_input = create_graph_state(
        url=amazon_url,
        task_id=task_id,
        max_products=max_products,
        max_competitive=max_competitive,
    )

    logger.info(f"Starting multi-agent analysis for URL: {amazon_url}")
    logger.info(
        f"Max products: {max_products}, Max competitive products: {max_competitive}"
    )

    # Run the workflow using the synchronous wrapper
    return run_workflow(initial_input)


async def run_analysis_async(
    amazon_url: str,
    task_id: str,
    max_products: int = 10,
    max_competitive: int = 5,
):
    """
    Run the multi-agent product analysis workflow asynchronously.

    Args:
        amazon_url: URL of the Amazon product to analyze
        task_id: Task ID for existing task
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to analyze

    Returns:
        The final state of the workflow execution
    """
    from langchain_app.workflow.multi_agent_graph import run_workflow_async

    # Prepare the initial input state
    initial_input = create_graph_state(
        url=amazon_url,
        task_id=task_id,
        max_products=max_products,
        max_competitive=max_competitive,
    )

    logger.info(f"Starting multi-agent analysis for URL: {amazon_url}")
    logger.info(
        f"Max products: {max_products}, Max competitive products: {max_competitive}"
    )

    return await run_workflow_async(initial_input)


def result_formatter(final_state: GraphState):
    """Format the analysis results into a string."""
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

    # Build report as a string
    report = f"\n{border}\n"
    report += f"AMAZON PRODUCT ANALYSIS REPORT - {timestamp}\n"
    report += f"{border}\n\n"

    # 1. Main Product Information
    if main_product:
        report += "📦 MAIN PRODUCT INFORMATION\n"
        report += section_border + "\n"
        report += f"Title: {main_product.title}\n"
        report += f"Price: ${main_product.price if hasattr(main_product, 'price') else 'N/A'}\n"
        report += (
            f"URL: {main_product.url if hasattr(main_product, 'url') else 'N/A'}\n"
        )
        # Add rating and review count
        if main_product.product_info.reviews:
            ratings = []
            for review in main_product.product_info.reviews:
                ratings.append(float(review.rating))
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            report += f"Rating: {avg_rating:.1f} ⭐ ({len(main_product.product_info.reviews)} reviews)\n"

        if main_product.product_info.details.categories:
            report += "\nCategories:\n"
            for i, feature in enumerate(
                main_product.product_info.details.categories[:5], 1
            ):
                report += f"  {i}. {feature}\n"
        report += "\n"

    # 2. Market Analysis
    report += "📊 MARKET ANALYSIS\n"
    report += section_border + "\n"

    if isinstance(market_analysis, dict):
        # Market position
        if "market_position" in market_analysis:
            report += f"Market Position: {market_analysis['market_position']}\n"

        # Competitive advantages
        if (
            "competitive_advantages" in market_analysis
            and market_analysis["competitive_advantages"]
        ):
            report += "\nCompetitive Advantages:\n"
            for i, adv in enumerate(market_analysis["competitive_advantages"], 1):
                report += f"  ✓ {adv}\n"

        # Competitive disadvantages
        if (
            "competitive_disadvantages" in market_analysis
            and market_analysis["competitive_disadvantages"]
        ):
            report += "\nCompetitive Disadvantages:\n"
            for i, disadv in enumerate(market_analysis["competitive_disadvantages"], 1):
                report += f"  ✗ {disadv}\n"

        # Price positioning
        if (
            "price_positioning" in market_analysis
            and market_analysis["price_positioning"]
        ):
            report += "\nPrice Positioning:\n"
            price_data = market_analysis["price_positioning"]
            if isinstance(price_data, dict):
                for key, value in price_data.items():
                    report += f"  • {key}: {value}\n"
            else:
                report += f"  • {price_data}\n"
    elif isinstance(market_analysis, str):
        report += market_analysis
    elif isinstance(market_analysis, list):
        for item in market_analysis:
            report += item
            report += "\n"
    else:
        report += "No detailed market analysis available.\n"
    report += "\n"

    # 3. Competitive Products Summary
    report += "🔍 COMPETITIVE PRODUCTS SUMMARY\n"
    report += section_border + "\n"
    report += f"Number of competitive products analyzed: {len(competitive_products)}\n"

    if competitive_products:
        report += "\nTop Competitors:\n"
        for i, product in enumerate(competitive_products[:3], 1):
            report += f"  {i}. {product.title if hasattr(product, 'title') else 'Unnamed Product'}\n"
            report += f"     Price: ${product.price if hasattr(product, 'price') else 'N/A'}\n"
            ratings = []
            for review in product.product_info.reviews:
                ratings.append(float(review.rating))
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            report += f"     Rating: {avg_rating:.1f} ⭐ ({len(product.product_info.reviews)} reviews)\n"
    report += "\n"

    # 4. Optimization Suggestions
    report += "💡 OPTIMIZATION SUGGESTIONS\n"
    report += section_border + "\n"

    if optimization_suggestions:
        report += optimization_suggestions
    else:
        report += "No optimization suggestions available.\n"
    report += "\n"

    # 5. Report Summary
    report += "📝 REPORT SUMMARY\n"
    report += section_border + "\n"
    report += f"Analysis completed at: {timestamp}\n"
    report += f"Products analyzed: {len(competitive_products) + 1} (1 main + {len(competitive_products)} competitive)\n"

    # Find the final summary message if available
    summary_message = ""
    for message in reversed(messages):
        if "summary" in message.lower() and len(message) > 50:
            summary_message = message
            break

    if summary_message:
        report += "\nExecutive Summary:\n"
        report += f"{summary_message}\n"

    report += f"\n{border}\n"
    report += "End of Report\n"
    report += f"{border}\n"

    return report
