"""Base agent class for Amazon product analysis agents."""

import logging
from typing import Any, Dict, List
from langchain_app.workflow.state import GraphState

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, name: str):
        """Initialize the agent.
        
        Args:
            name: The name of the agent
        """
        self.name = name
        logger.info(f"Initialized {name} agent")
    
    async def process(self, state: GraphState) -> GraphState:
        """Process the current state and return an updated state.
        
        This method should be implemented by all agent subclasses.
        
        Args:
            state: The current workflow state
            
        Returns:
            Updated state after processing
        """
        raise NotImplementedError("Subclasses must implement the process method")
    
    def _add_message(self, state: GraphState, message: str) -> None:
        """Add a message to the state's message list with agent attribution.
        
        Args:
            state: The current state
            message: The message to add
        """
        state["messages"].append(f"[{self.name}] {message}")
        logger.info(f"[{self.name}] {message}")
