"""Supervisor Agent for coordinating the multi-agent workflow."""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_app.agents.base_agent import BaseAgent
from langchain_app.workflow.state import GraphState
from langchain_app.core.logging_utils import configure_logger
from langchain_app.core.config import (
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    WORKFLOW_END
)

# Configure logger
logger = configure_logger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Agent responsible for coordinating the workflow between specialized agents.

    This agent:
    1. Determines which agent should run next based on workflow state
    2. Tracks overall progress of the analysis
    3. Ensures all required workflow steps are completed
    """

    def __init__(self, model=DEFAULT_LLM_MODEL, temperature=DEFAULT_LLM_TEMPERATURE):
        """Initialize the supervisor agent."""
        super().__init__("SupervisorAgent", model=model, temperature=temperature)

        # Set up the supervisor prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            You are the supervisor of a multi-agent product analysis workflow.  
            Your role is to:
            1. Ensure that the final report contains all required sections:
               • Product Status Analysis (price, rating, key features)  
               • Competitive Product Analysis (strengths & weaknesses)  
               • Market Positioning Recommendations  
               • Product Optimization Strategies (title, description, pricing, etc.)  
            2. Coordinate which specialized agent should run next.
            3. Monitor progress and mark the workflow complete once every section is covered.

            Current state: {state}
            """,
                ),
                ("human", "{input}"),
            ]
        )

    async def process(self, state: GraphState) -> GraphState:
        """Process workflow coordination tasks.

        Args:
            state: Current workflow state

        Returns:
            Updated state with next agent decision
        """
        self._add_message(state, "Evaluating workflow progress")

        # Use the LLM to help evaluate the state and make decisions
        # prompt_args = {
        #     "state": self._format_state_for_prompt(state),
        #     "input": "Analyze the current state and recommend which agent should run next.",
        # }

        # llm_response = await self._run_llm(prompt_args)
        # self._add_message(state, f"Analysis: {llm_response}")

        # Determine which agent should run next
        next_agent = self.decide_next_agent(state)
        state["current_agent"] = next_agent

        # Check if workflow is complete
        if next_agent == "END":
            state["task_complete"] = True
            self._add_message(state, "Analysis workflow complete")
            await self._generate_summary(state)
        else:
            self._add_message(state, f"Selected next agent: {next_agent}")

        return state

    def _format_state_for_prompt(self, state: GraphState) -> str:
        """Format the state into a string summary for the prompt.

        Args:
            state: Current workflow state

        Returns:
            String summary of the current state
        """
        summary_parts = []

        # Add main product info
        if state.get("main_product"):
            main_product = state["main_product"]
            summary_parts.append(
                f"Main product: {main_product.title} (Price: {main_product.price})"
            )
        else:
            summary_parts.append("Main product: Not collected yet")

        # Add competitive products info
        competitive_products = state.get("competitive_products", [])
        summary_parts.append(
            f"Competitive products: {len(competitive_products)} collected"
        )

        # Add market analysis info
        if state.get("market_analysis"):
            summary_parts.append("Market analysis: Complete")
        else:
            summary_parts.append("Market analysis: Not complete")

        # Add optimization suggestions info
        if state.get("optimization_suggestions"):
            summary_parts.append("Optimization suggestions: Complete")
        else:
            summary_parts.append("Optimization suggestions: Not complete")

        # Add error info if present
        if state.get("error"):
            summary_parts.append(f"Error: {state['error']}")

        return "\n".join(summary_parts)

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
            return WORKFLOW_END

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
        return WORKFLOW_END

    async def _generate_summary(self, state: GraphState) -> None:
        """Generate a final summary of the analysis workflow using the LLM.

        Args:
            state: Current workflow state
        """
        main_product = state.get("main_product")
        if not main_product:
            self._add_message(
                state, "Unable to generate summary: Main product not available"
            )
            return

        # Use the LLM to generate a comprehensive summary
        prompt_args = {
            "state": self._format_state_for_prompt(state),
            "input": "Generate a comprehensive final report summarizing all aspects of the product analysis.",
        }

        llm_summary = await self._run_llm(prompt_args)

        # Add the LLM-generated summary to messages
        self._add_message(state, "# Amazon Product Analysis - Final Report")
        self._add_message(state, llm_summary)
