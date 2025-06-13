"""Optimization Advisor Agent for Amazon product analysis."""

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


class OptimizationAdvisorAgent(BaseAgent):
    """
    Agent responsible for generating optimization suggestions based on market analysis.
    
    This agent handles:
    1. Suggesting product improvements
    2. Recommending pricing strategies
    3. Identifying content optimization opportunities
    4. Proposing marketing strategies
    """
    
    def __init__(self):
        """Initialize the optimization advisor agent."""
        super().__init__("OptimizationAdvisorAgent")
    
    async def process(self, state: GraphState) -> GraphState:
        """Process optimization advisory tasks.
        
        Steps:
        1. Check if market analysis is complete
        2. Generate optimization suggestions based on analysis
        3. Prioritize suggestions by estimated impact
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with optimization suggestions
        """
        self._add_message(state, "Starting optimization advisory process")
        
        # Check if we have the necessary data
        main_product = state.get("main_product")
        market_analysis = state.get("market_analysis")
        
        if not main_product:
            state["error"] = "Main product not available for optimization"
            self._add_message(state, state["error"])
            return state
        
        if not market_analysis:
            state["error"] = "Market analysis not available for optimization"
            self._add_message(state, state["error"])
            return state
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_suggestions(state)
        state["optimization_suggestions"] = optimization_suggestions
        
        # Add summary to messages
        self._add_message(state, "## Optimization Recommendations")
        for category, suggestions in optimization_suggestions.items():
            self._add_message(state, f"\n### {category}")
            for suggestion in suggestions:
                self._add_message(state, f"- {suggestion}")
        
        self._add_message(state, "Optimization advisory process complete")
        return state
    
    def _generate_suggestions(self, state: GraphState) -> Dict[str, List[str]]:
        """Generate optimization suggestions based on market analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dictionary of optimization suggestions by category
        """
        logger.info("Generating optimization suggestions")
        
        main_product = state.get("main_product")
        market_analysis = state.get("market_analysis", {})
        competitive_products = state.get("competitive_products", [])
        
        # Initialize suggestions structure
        suggestions = {
            "Product Improvements": [],
            "Pricing Strategy": [],
            "Content Optimization": [],
            "Marketing Strategy": []
        }
        
        # Add product improvement suggestions based on feature gaps
        feature_gaps = market_analysis.get("feature_gaps", [])
        for feature in feature_gaps[:3]:  # Limit to top 3
            suggestions["Product Improvements"].append(f"Consider adding '{feature}' to match competitor offerings")
        
        # If no feature gaps identified, add a general suggestion
        if not feature_gaps:
            suggestions["Product Improvements"].append("Conduct detailed feature analysis against top competitors to identify improvement opportunities")
        
        # Add pricing strategy suggestions
        market_position = market_analysis.get("market_position", "unknown")
        main_price = market_analysis.get("main_product_price", 0)
        avg_competitor_price = market_analysis.get("avg_competitor_price", 0)
        
        if market_position == "premium":
            suggestions["Pricing Strategy"].append("Ensure premium pricing is justified with clear value proposition")
            suggestions["Pricing Strategy"].append("Highlight premium features to support higher price point")
            
        elif market_position == "budget":
            suggestions["Pricing Strategy"].append("Evaluate if price can be increased without affecting conversion rate")
            suggestions["Pricing Strategy"].append("Consider promotional bundles to increase average order value")
            
        elif market_position == "mid-range":
            price_diff_percent = ((main_price - avg_competitor_price) / avg_competitor_price) * 100 if avg_competitor_price else 0
            
            if price_diff_percent > 5:
                suggestions["Pricing Strategy"].append(f"Current price is {price_diff_percent:.1f}% above average - ensure differentiation is clear")
            elif price_diff_percent < -5:
                suggestions["Pricing Strategy"].append(f"Current price is {-price_diff_percent:.1f}% below average - potential opportunity to increase margin")
            else:
                suggestions["Pricing Strategy"].append("Price is aligned with market average - consider dynamic pricing strategy based on demand")
        
        # Add content optimization suggestions
        suggestions["Content Optimization"].append("Ensure product title includes main keywords and distinguishing features")
        
        # Add distinguishing features to description if available
        distinguishing_features = market_analysis.get("distinguishing_features", [])
        if distinguishing_features:
            suggestions["Content Optimization"].append(f"Highlight distinguishing features prominently: {', '.join(distinguishing_features[:3])}")
        
        # Add marketing strategy suggestions
        competitive_advantages = market_analysis.get("competitive_advantages", [])
        if competitive_advantages:
            advantages_str = "; ".join(competitive_advantages[:3])
            suggestions["Marketing Strategy"].append(f"Focus marketing messaging on key advantages: {advantages_str}")
        
        # Add generic marketing suggestions if no specific advantages
        if len(suggestions["Marketing Strategy"]) == 0:
            suggestions["Marketing Strategy"].append("Develop unique selling proposition to differentiate from competitors")
        
        # Add A/B testing recommendation for content
        suggestions["Marketing Strategy"].append("Implement A/B testing for product images and description variants")
        
        return suggestions
