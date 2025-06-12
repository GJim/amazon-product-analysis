"""State definition for the Amazon product analysis workflow."""

from typing import TypedDict, Annotated, List, Optional
import operator

from langchain_app.core.models import Product
from langchain_app.core.collector import ProductCollector


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
