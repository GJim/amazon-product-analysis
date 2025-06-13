"""Market Analyzer Agent for Amazon product analysis."""

import logging
from typing import Dict, Any, List
from langchain_app.agents.base_agent import BaseAgent
from langchain_app.workflow.state import GraphState
from langchain_app.core.models import Product

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarketAnalyzerAgent(BaseAgent):
    """
    Agent responsible for analyzing market data and competitive products.
    
    This agent handles:
    1. Analyzing the main product features and pricing
    2. Analyzing competitive products 
    3. Generating market position analysis
    4. Identifying competitive advantages and disadvantages
    """
    
    def __init__(self):
        """Initialize the market analyzer agent."""
        super().__init__("MarketAnalyzerAgent")
    
    async def process(self, state: GraphState) -> GraphState:
        """Process market analysis tasks.
        
        Steps:
        1. Check if data collection is complete
        2. Analyze main product features
        3. Compare with competitive products
        4. Generate market positioning analysis
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with market analysis
        """
        self._add_message(state, "Starting market analysis process")
        
        # Check if we have the necessary data
        main_product = state.get("main_product")
        competitive_products = state.get("competitive_products", [])
        
        if not main_product:
            state["error"] = "Main product not available for analysis"
            self._add_message(state, state["error"])
            return state
        
        if not competitive_products:
            self._add_message(state, "Warning: No competitive products available. Analysis may be limited.")
        
        # Generate market analysis
        market_analysis = self._analyze_market(main_product, competitive_products)
        state["market_analysis"] = market_analysis
        
        # Add summary to messages
        analysis_summary = self._generate_analysis_summary(market_analysis)
        for line in analysis_summary:
            self._add_message(state, line)
        
        self._add_message(state, "Market analysis process complete")
        return state
    
    def _analyze_market(self, main_product: Product, competitive_products: List[Product]) -> Dict[str, Any]:
        """Analyze the market based on collected product data.
        
        Args:
            main_product: The main product being analyzed
            competitive_products: List of competitive products
            
        Returns:
            Dictionary containing market analysis data
        """
        logger.info("Generating market analysis")
        
        # Calculate average price of competitors
        competitor_prices = []
        for product in competitive_products:
            try:
                # Extract numeric price
                price_str = product.price.replace('$', '').replace(',', '')
                price = float(price_str)
                competitor_prices.append(price)
            except (ValueError, AttributeError):
                # Skip products with unparseable prices
                pass
        
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0
        
        # Determine main product price
        main_price = 0
        try:
            price_str = main_product.price.replace('$', '').replace(',', '')
            main_price = float(price_str)
        except (ValueError, AttributeError):
            pass
        
        # Price positioning analysis
        price_position = "unknown"
        if main_price > 0 and competitor_prices:
            if main_price > 1.2 * avg_competitor_price:
                price_position = "premium"
            elif main_price < 0.8 * avg_competitor_price:
                price_position = "budget"
            else:
                price_position = "mid-range"
        
        # Analyze product features
        main_features = []
        if main_product.product_info.details and main_product.product_info.details.specifications:
            main_features = list(main_product.product_info.details.specifications.keys())
        
        # Identify common and distinguishing features
        all_competitor_features = []
        for product in competitive_products:
            if product.product_info.details and product.product_info.details.specifications:
                all_competitor_features.extend(list(product.product_info.details.specifications.keys()))
        
        # Count feature frequency
        feature_frequency = {}
        for feature in all_competitor_features:
            feature_frequency[feature] = feature_frequency.get(feature, 0) + 1
        
        # Identify distinguishing features of main product
        distinguishing_features = []
        for feature in main_features:
            if feature not in feature_frequency or feature_frequency[feature] < len(competitive_products) / 2:
                distinguishing_features.append(feature)
        
        # Identify feature gaps (features present in >50% of competitors but not in main product)
        feature_gaps = []
        for feature, count in feature_frequency.items():
            if count > len(competitive_products) / 2 and feature not in main_features:
                feature_gaps.append(feature)
        
        # Prepare competitive advantages and disadvantages
        competitive_advantages = []
        competitive_disadvantages = []
        
        # Add price positioning as advantage/disadvantage
        if price_position == "premium":
            competitive_advantages.append("Premium pricing suggests higher quality perception")
            competitive_disadvantages.append("Higher price point may deter budget-conscious customers")
        elif price_position == "budget":
            competitive_advantages.append("Lower price point may attract cost-conscious customers")
            competitive_disadvantages.append("Lower price may signal lower quality to some customers")
        
        # Add distinguishing features as advantages
        for feature in distinguishing_features[:3]:  # Limit to top 3
            competitive_advantages.append(f"Unique feature: {feature}")
        
        # Add feature gaps as disadvantages
        for feature in feature_gaps[:3]:  # Limit to top 3
            competitive_disadvantages.append(f"Missing feature: {feature}")
        
        # Create market analysis dictionary
        market_analysis = {
            "market_position": price_position,
            "avg_competitor_price": avg_competitor_price,
            "main_product_price": main_price,
            "competitive_advantages": competitive_advantages,
            "competitive_disadvantages": competitive_disadvantages,
            "distinguishing_features": distinguishing_features,
            "feature_gaps": feature_gaps,
            "analyzed_competitors": len(competitive_products)
        }
        
        return market_analysis
    
    def _generate_analysis_summary(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate a summary of the market analysis for display.
        
        Args:
            analysis: The market analysis dictionary
            
        Returns:
            List of strings representing the analysis summary
        """
        summary = [
            "## Market Analysis Summary",
            f"- Market Position: {analysis.get('market_position', 'Unknown').capitalize()}",
            f"- Analyzed {analysis.get('analyzed_competitors', 0)} competitive products"
        ]
        
        # Add price analysis
        summary.append("\n### Price Analysis")
        summary.append(f"- Main Product Price: ${analysis.get('main_product_price', 0):.2f}")
        summary.append(f"- Average Competitor Price: ${analysis.get('avg_competitor_price', 0):.2f}")
        
        # Add competitive advantages
        if analysis.get("competitive_advantages"):
            summary.append("\n### Competitive Advantages")
            for advantage in analysis.get("competitive_advantages", []):
                summary.append(f"- {advantage}")
        
        # Add competitive disadvantages
        if analysis.get("competitive_disadvantages"):
            summary.append("\n### Competitive Disadvantages")
            for disadvantage in analysis.get("competitive_disadvantages", []):
                summary.append(f"- {disadvantage}")
        
        return summary
