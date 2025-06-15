"""Data Collector Agent for gathering Amazon product data."""

import logging
import asyncio
from typing import List, Dict, Any, Optional

from langchain_core.prompts import ChatPromptTemplate

from langchain_app.agents.base_agent import BaseAgent
from langchain_app.core.collector import ProductCollector
from langchain_app.core.models import Product
from langchain_app.workflow.state import GraphState
from workers.sinker import create_product

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataCollectorAgent(BaseAgent):
    """
    Agent responsible for collecting product data from Amazon.

    This agent:
    1. Initializes the ProductCollector
    2. Collects main product data
    3. Collects competitive product data
    """

    def __init__(self, model="gpt-4o", temperature=0):
        """Initialize the data collector agent."""
        super().__init__("DataCollectorAgent", model=model, temperature=temperature)

        # Set up the data collector prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            You are a data collection expert. Your objectives:
            1. Gather **Product Status Analysis** data for the main product:
               • Current price  
               • Average rating and review count  
               • Key features and specifications
            2. Identify 3–5 top competitors in the same category.
            3. For each competitor, collect the same status metrics (price, rating, features).
            Use the provided tools (`amazon_scraper`, `amazon_search`) to fetch all data.
            """,
                ),
                ("human", "Collect data for product: {main_product}"),
            ]
        )

    async def process(self, state: GraphState) -> GraphState:
        """Process data collection tasks.

        Args:
            state: Current workflow state

        Returns:
            Updated state with collected product data
        """
        self._add_message(state, "Starting data collection process")

        try:
            # Step 1: Initialize the collector if it doesn't exist
            if not state.get("collector"):
                await self._init_collector(state)

            # Step 2: Collect main product if it doesn't exist
            if not state.get("main_product") and state.get("collector"):
                await self._collect_main_product(state)

            # Step 3: Collect competitive products if main product exists but no competitive products
            if (
                state.get("main_product")
                and not state.get("competitive_products")
                and state.get("collector")
            ):
                await self._collect_competitive_products(state)

            # Get guidance from the LLM on data organization and analysis focusing
            if state.get("main_product") and state.get("competitive_products"):
                await self._get_data_organization_guidance(state)

            self._add_message(state, "Data collection completed successfully")
            return state

        except Exception as e:
            error_msg = f"Error during data collection: {str(e)}"
            logger.error(error_msg)
            state["error"] = error_msg
            self._add_message(state, error_msg)
            return state

    async def _get_data_organization_guidance(self, state: GraphState) -> None:
        """Get guidance from the LLM on organizing the collected data.

        Args:
            state: Current workflow state
        """
        main_product = state.get("main_product")
        competitive_products = state.get("competitive_products", [])

        if not main_product or not competitive_products:
            return

        # Format product info for the LLM
        main_product_info = {
            "title": main_product.title,
            "price": main_product.price,
            "features": (
                main_product.features if hasattr(main_product, "features") else []
            ),
            "rating": main_product.rating if hasattr(main_product, "rating") else None,
        }

        # Use the LLM to provide guidance on data organization
        prompt_args = {
            "main_product": main_product_info,
        }

        llm_response = await self._run_llm(prompt_args)
        self._add_message(state, f"Data organization guidance: {llm_response}")

    async def _init_collector(self, state: GraphState) -> None:
        """Initialize the product collector.

        Args:
            state: Current workflow state
        """

        self._add_message(state, "Initializing product collector")

        # Initialize the collector
        collector = ProductCollector()
        state["collector"] = collector

        self._add_message(state, "Product collector initialized")

    async def _collect_main_product(self, state: GraphState) -> None:
        """Collect data for the main product.

        Args:
            state: Current workflow state
        """

        url = state.get("url")
        if not url:
            raise ValueError("No URL provided in the state")

        collector: ProductCollector = state.get("collector")
        if not collector:
            raise ValueError("Product collector not initialized")

        self._add_message(state, "Collecting main product data")

        # Scrape the main product asynchronously
        main_product = await collector.collect_product_async(url, is_main_product=True)

        # Save the main product to the database
        create_product.delay(main_product.product_info.model_dump())

        state["main_product"] = main_product

        self._add_message(
            state,
            f"Main product collected: {main_product.title} (Price: {main_product.price})",
        )

    async def _collect_competitive_products(self, state: GraphState) -> None:
        """Collect data for competitive products.

        Args:
            state: Current workflow state
        """
        collector = state.get("collector")
        main_product = state.get("main_product")
        max_products = state.get("max_products", 10)
        max_competitive = state.get("max_competitive", 5)

        if not collector or not main_product:
            raise ValueError("Collector or main product not available")

        if collector.url_queue.empty():
            raise ValueError("Can't collect competitive products: no URLs available")

        self._add_message(
            state,
            f"Collecting competitive products (max {max_competitive} out of {max_products})",
        )

        # Collect competitive products asynchronously
        competitive_products = await collector.collect_competitive_products_async(
            main_product=main_product,
        )

        # Save the competitive products to the database
        for competitive_product in competitive_products:
            create_product.delay(competitive_product.product_info.model_dump())

        state["competitive_products"] = competitive_products

        self._add_message(
            state, f"Collected {len(competitive_products)} competitive products"
        )
