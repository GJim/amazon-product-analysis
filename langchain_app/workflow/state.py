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
    """

    url: str
    collector: ProductCollector
    main_product: Optional[Product]
    competitive_products: List[Product]
    market_analysis: Optional[Dict[str, Any]]
    optimization_suggestions: List[str]
    messages: Annotated[list, operator.add]
    error: Optional[str]
    current_agent: str
    max_products: int
    max_competitive: int
    task_complete: bool
