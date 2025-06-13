"""Data Collector Agent for Amazon product analysis."""

import asyncio
import logging
from langchain_app.agents.base_agent import BaseAgent
from langchain_app.workflow.state import GraphState
from langchain_app.core.collector import ProductCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataCollectorAgent(BaseAgent):
    """
    Agent responsible for collecting product data from Amazon.
    
    This agent handles:
    1. Initializing the product collector
    2. Collecting the main product data
    3. Collecting competitive products data
    """
    
    def __init__(self):
        """Initialize the data collector agent."""
        super().__init__("DataCollectorAgent")
    
    async def process(self, state: GraphState) -> GraphState:
        """Process data collection tasks.
        
        Steps:
        1. Initialize collector if not present
        2. Collect main product if not present
        3. Collect competitive products if main product is present
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with collected data
        """
        self._add_message(state, "Starting data collection process")
        
        # Initialize collector if not present
        if "collector" not in state:
            state = await self._initialize_collector(state)
        
        # Collect main product if not present
        if not state.get("main_product"):
            state = await self._collect_main_product(state)
            
            # If there was an error collecting the main product, return early
            if state.get("error"):
                return state
        
        # Collect competitive products
        if state.get("main_product") and not state.get("competitive_products"):
            state = await self._collect_competitive_products(state)
        
        self._add_message(state, "Data collection process complete")
        return state
    
    async def _initialize_collector(self, state: GraphState) -> GraphState:
        """Initialize the product collector."""
        self._add_message(state, "Initializing product collector")
        
        # Get configuration parameters from state with defaults
        max_products = state.get("max_products", 10)
        max_competitive = state.get("max_competitive", 5)
        min_competitive = min(3, max_competitive)
        
        # Create collector with configuration
        collector = ProductCollector()
        collector.max_products = max_products
        collector.max_competitive_products = max_competitive
        collector.min_competitive_products = min_competitive
        
        state["collector"] = collector
        self._add_message(state, f"Product collector initialized (max products: {max_products}, max competitive: {max_competitive})")
        state["competitive_products"] = []
        return state
    
    async def _collect_main_product(self, state: GraphState) -> GraphState:
        """Collect the main product information."""
        url = state["url"]
        collector = state["collector"]
        
        self._add_message(state, f"Collecting main product from URL: {url}")
        
        # Validate URL
        if not collector.is_valid_amazon_url(url):
            state["error"] = f"Invalid Amazon URL: {url}"
            self._add_message(state, state["error"])
            return state
        
        # Collect main product asynchronously
        main_product = await collector.collect_product_async(url, is_main_product=True)
        
        if not main_product:
            state["error"] = f"Failed to collect main product from URL: {url}"
            self._add_message(state, state["error"])
            return state
        
        state["main_product"] = main_product
        self._add_message(state, f"Successfully collected main product: {main_product.title}")
        
        # Add similar items to queue for competitive product collection
        for similar_url in main_product.similar_items_links:
            collector.url_queue.put(similar_url)
        
        self._add_message(state, f"Added {len(main_product.similar_items_links)} competitive product URLs to queue")
        return state
    
    async def _collect_competitive_products(self, state: GraphState) -> GraphState:
        """Collect information about competitive products."""
        collector = state["collector"]
        main_product = state["main_product"]
        
        if not main_product:
            state["error"] = "Main product not available"
            self._add_message(state, state["error"])
            return state
        
        self._add_message(state, "Collecting competitive products")
        
        try:
            state["competitive_products"] = await collector.collect_competitive_products_async(main_product)
        except Exception as e:
            state["error"] = f"Error collecting competitive products: {str(e)}"
            self._add_message(state, state["error"])
            return state
        
        self._add_message(state, f"Selected {len(state['competitive_products'])} most distinguishing competitive products")
        return state
