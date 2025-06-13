"""Supervisor Agent for coordinating the multi-agent workflow."""

import logging
from typing import Dict, Any
from langchain_app.agents.base_agent import BaseAgent
from langchain_app.workflow.state import GraphState

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Agent responsible for coordinating the workflow between specialized agents.
    
    This agent:
    1. Determines which agent should run next based on workflow state
    2. Tracks overall progress of the analysis
    3. Ensures all required workflow steps are completed
    """
    
    def __init__(self):
        """Initialize the supervisor agent."""
        super().__init__("SupervisorAgent")
    
    async def process(self, state: GraphState) -> GraphState:
        """Process workflow coordination tasks.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with next agent decision
        """
        self._add_message(state, "Evaluating workflow progress")
        
        # Determine which agent should run next
        next_agent = self.decide_next_agent(state)
        state["current_agent"] = next_agent
        
        # Check if workflow is complete
        if next_agent == "END":
            state["task_complete"] = True
            self._add_message(state, "Analysis workflow complete")
            self._generate_summary(state)
        else:
            self._add_message(state, f"Selected next agent: {next_agent}")
        
        return state
    
    def decide_next_agent(self, state: GraphState) -> str:
        """Determine which agent should run next based on current state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Name of the next agent to run, or "END" if workflow is complete
        """
        # Check for errors - end workflow if error is present
        if state.get("error"):
            logger.info("Error detected in workflow, ending process")
            return "END"
        
        # Check workflow progression and determine next agent
        
        # If we don't have main product or competitive products, run data collector
        if not state.get("main_product") or not state.get("competitive_products"):
            logger.info("Product data collection needed")
            return "data_collector"
        
        # If we have products but no market analysis, run market analyzer
        if not state.get("market_analysis"):
            logger.info("Market analysis needed")
            return "market_analyzer"
        
        # If we have market analysis but no optimization suggestions, run optimization advisor
        if not state.get("optimization_suggestions"):
            logger.info("Optimization suggestions needed")
            return "optimization_advisor"
        
        # All tasks completed
        logger.info("All workflow tasks completed")
        return "END"
    
    def _generate_summary(self, state: GraphState) -> None:
        """Generate a final summary of the analysis workflow.
        
        Args:
            state: Current workflow state
        """
        main_product = state.get("main_product")
        if not main_product:
            self._add_message(state, "Unable to generate summary: Main product not available")
            return
        
        summary = [
            "# Amazon Product Analysis - Final Report",
            f"\n## Analyzed Product: {main_product.title}",
            f"- Price: {main_product.price}",
            f"- ASIN: {main_product.asin}",
        ]
        
        # Add market analysis summary
        market_analysis = state.get("market_analysis", {})
        if market_analysis:
            summary.append("\n## Market Position Summary")
            summary.append(f"- Position: {market_analysis.get('market_position', 'Unknown').capitalize()}")
            summary.append(f"- Competitive Advantages: {len(market_analysis.get('competitive_advantages', []))}")
            summary.append(f"- Competitive Disadvantages: {len(market_analysis.get('competitive_disadvantages', []))}")
        
        # Add optimization summary
        optimization_suggestions = state.get("optimization_suggestions", {})
        if optimization_suggestions:
            summary.append("\n## Optimization Opportunities")
            for category, suggestions in optimization_suggestions.items():
                summary.append(f"- {category}: {len(suggestions)} suggestions")
        
        # Add analysis scale
        competitive_products = state.get("competitive_products", [])
        summary.append(f"\n## Analysis Scale: {len(competitive_products)} competitive products analyzed")
        
        # Add summary to messages
        self._add_message(state, "\n".join(summary))
