"""Multi-agent graph definition for the Amazon product analysis workflow."""

import logging
import asyncio
from typing import Dict
from langchain_app.database.operations import create_task_record

from langgraph.graph import StateGraph, END

from langchain_app.workflow.state import GraphState
from langchain_app.agents.supervisor_agent import SupervisorAgent
from langchain_app.agents.collector_agent import DataCollectorAgent
from langchain_app.agents.analyzer_agent import MarketAnalyzerAgent
from langchain_app.agents.advisor_agent import OptimizationAdvisorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_multi_agent_workflow():
    """Create and configure the multi-agent workflow graph."""
    # Initialize the graph
    workflow = StateGraph(GraphState)

    # Initialize agents
    supervisor = SupervisorAgent(model="gpt-4.1-nano")
    data_collector = DataCollectorAgent(model="gpt-4.1-nano")
    market_analyzer = MarketAnalyzerAgent(model="gpt-4.1-nano")
    optimization_advisor = OptimizationAdvisorAgent(model="gpt-4.1-nano")

    # Define node functions
    async def supervisor_node(state: GraphState) -> GraphState:
        """Supervisor agent node function."""
        return await supervisor.process(state)

    async def data_collector_node(state: GraphState) -> GraphState:
        """Data collector agent node function."""
        return await data_collector.process(state)

    async def market_analyzer_node(state: GraphState) -> GraphState:
        """Market analyzer agent node function."""
        return await market_analyzer.process(state)

    async def optimization_advisor_node(state: GraphState) -> GraphState:
        """Optimization advisor agent node function."""
        return await optimization_advisor.process(state)

    # Add nodes to the graph
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("data_collector", data_collector_node)
    workflow.add_node("market_analyzer", market_analyzer_node)
    workflow.add_node("optimization_advisor", optimization_advisor_node)

    # Set the entry point
    workflow.set_entry_point("supervisor")

    # Add conditional edges based on supervisor decision
    def route_to_agent(state: GraphState) -> str:
        """Route to the appropriate agent based on current_agent field."""
        return state.get("current_agent", "supervisor")

    # Add conditional edges from supervisor to agents
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "data_collector": "data_collector",
            "market_analyzer": "market_analyzer",
            "optimization_advisor": "optimization_advisor",
            "END": END,
        },
    )

    # Add edges back to supervisor after each agent
    workflow.add_edge("data_collector", "supervisor")
    workflow.add_edge("market_analyzer", "supervisor")
    workflow.add_edge("optimization_advisor", "supervisor")

    # Compile the graph
    return workflow.compile()


# Helper function to run the workflow with asyncio
async def run_workflow_async(state: Dict) -> Dict:
    """Run the workflow asynchronously.

    Args:
        state: Initial state dictionary

    Returns:
        Final state after workflow completion
    """
    # Create or validate task record if needed
    url = state.get("url")
    task_id = state.get("task_id")
    max_products = state.get("max_products", 10)
    max_competitive = state.get("max_competitive", 5)

    # Create task record
    if url and task_id:
        task_result = create_task_record(
            url=url, max_product=max_products, max_competitive=max_competitive
        )

        if task_result.get("status") == "success":
            db_task_id = task_result.get("db_task_id")
            state["db_task_id"] = db_task_id
            logger.info(f"Created task with ID: {db_task_id}")
        else:
            logger.warning(f"Failed to create task: {task_result.get('error')}")

    app = create_multi_agent_workflow()

    # Execute the workflow with async streaming for monitoring progress
    final_state = None
    async for current_state in app.astream(state):
        final_state = current_state
        current_agent = current_state.get("current_agent", "Unknown")
        logger.info(f"Current agent: {current_agent}")

    return final_state


# Synchronous wrapper for the async workflow
def run_workflow(state: Dict) -> Dict:
    """Run the workflow synchronously.

    Args:
        state: Initial state dictionary

    Returns:
        Final state after workflow completion
    """
    # Create or get the event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Run the workflow
    return loop.run_until_complete(run_workflow_async(state))
