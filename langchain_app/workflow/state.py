"""State definition for the Amazon product analysis multi-agent workflow."""

from typing import TypedDict, Annotated, List, Optional, Dict, Any
import operator

from langchain_app.core.models import Product
from langchain_app.core.collector import ProductCollector


class GraphState(TypedDict):
    """
    Represents the state of our multi-agent graph.

    Attributes:
        url: The initial Amazon product URL
        collector: The ProductCollector instance
        main_product: The main product being analyzed
        competitive_products: List of competitive products
        market_analysis: The market analysis data
        optimization_suggestions: List of optimization suggestions
        messages: List of messages for tracking progress
        error: Any error message
        current_agent: The currently active agent
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to collect
        task_complete: Whether the analysis task is complete
        task_id: The Celery task ID for Redis pub/sub channels
        db_task_id: The database task ID
        db_main_product_id: The database main product ID
        db_product_ids: Dictionary mapping product URLs to database IDs
    """

    url: str
    collector: ProductCollector
    main_product: Optional[Product]
    competitive_products: List[Product]
    market_analysis: Optional[str]
    optimization_suggestions: Optional[str]
    messages: Annotated[list, operator.add]
    error: Optional[str]
    current_agent: str
    max_products: int
    max_competitive: int
    task_complete: bool
    task_id: str
    db_task_id: Optional[int]
    db_main_product_id: Optional[int]


def create_graph_state(
    url: str, task_id: str, max_products: int = 10, max_competitive: int = 5
) -> GraphState:
    """
    Create a new GraphState instance with the given configuration.

    Args:
        url: The initial Amazon product URL
        max_products: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to collect
        task_id: The Celery task ID for Redis pub/sub channels

    Returns:
        A new GraphState instance
    """
    collector = ProductCollector()

    return {
        "url": url,
        "collector": collector,
        "main_product": None,
        "competitive_products": [],
        "market_analysis": None,
        "optimization_suggestions": None,
        "messages": [],
        "error": None,
        "current_agent": "supervisor",
        "max_products": max_products,
        "max_competitive": max_competitive,
        "task_complete": False,
        "task_id": task_id,
        "db_task_id": None,
        "db_main_product_id": None,
    }
