"""Graph definition for the Amazon product analysis workflow."""

from langgraph.graph import StateGraph, END

from langchain_app.workflow.state import GraphState
from langchain_app.workflow.nodes import (
    initialize_collector,
    scrape_main_product,
    collect_competitive_products,
    analyze_products,
    route_based_on_error,
    handle_error,
)


def create_workflow():
    """Create and configure the workflow graph."""
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
        {
            "analyze_products": "analyze_products",
            "handle_error": "handle_error",
        },
    )
    workflow.add_edge("analyze_products", END)
    workflow.add_edge("handle_error", END)

    # Compile the graph
    return workflow.compile()
