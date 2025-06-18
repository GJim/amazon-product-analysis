"""
Celery tasks for Amazon Product Analysis.
"""

import logging
from typing import Dict, Any
from celery import current_task

from workers.celery_app import celery_app
from langchain_app.main import run_analysis, result_formatter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.analyze_product")
def analyze_product(
    amazon_url: str, max_products: int = 10, max_competitive: int = 5
) -> Dict[str, Any]:
    """
    Task to analyze an Amazon product URL using the LangChain app.

    Args:
        amazon_url: URL of the Amazon product to analyze
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to analyze

    Returns:
        Dict containing analysis results
    """
    logger.info(f"Starting analysis for URL: {amazon_url}")
    logger.info(
        f"Parameters: max_products={max_products}, max_competitive={max_competitive}"
    )

    try:
        # Get the current task ID for Redis channel
        current_task_id = current_task.request.id

        if current_task_id:
            logger.info(f"Task ID: {current_task_id}")
        else:
            logger.warning("Task ID not found")

        # Run the analysis using the LangChain app
        final_state = run_analysis(
            amazon_url=amazon_url,
            task_id=current_task_id,
            max_products=max_products,
            max_competitive=max_competitive,
        )

        # Format the results
        # report = result_formatter(final_state["supervisor"])
        final_state = final_state["supervisor"]
        main_product = final_state.get("main_product")
        competitive_products = final_state.get("competitive_products", [])
        market_analysis = final_state.get("market_analysis", {})
        optimization_suggestions = final_state.get("optimization_suggestions", {})
        report = {
            "main_product": main_product.product_info.model_dump(),
            "competitive_products": [
                product.product_info.model_dump() for product in competitive_products
            ],
            "market_analysis": market_analysis,
            "optimization_suggestions": optimization_suggestions,
        }

        # Return both the structured data and formatted report
        return {"status": "success", "report": report}
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}
