"""Base agent class for Amazon product analysis agents."""

import logging
import os
from typing import Any, Dict, List, Optional

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langchain_app.workflow.state import GraphState

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, name: str, model: str = "gpt-4.1-nano", temperature: float = 0):
        """Initialize the agent.

        Args:
            name: The name of the agent
            model: The OpenAI model to use
            temperature: The temperature for generation
        """
        self.name = name
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.prompt = None  # Will be set by subclasses
        logger.info(f"Initialized {name} agent with model {model}")

    async def process(self, state: GraphState) -> GraphState:
        """Process the current state and return an updated state.

        This method should be implemented by all agent subclasses.

        Args:
            state: The current workflow state

        Returns:
            Updated state after processing
        """
        raise NotImplementedError("Subclasses must implement the process method")

    async def _run_llm(self, prompt_args: Dict[str, Any]) -> str:
        """Run the LLM with the agent's prompt.

        Args:
            prompt_args: Arguments to format the prompt with

        Returns:
            The LLM's response
        """
        if not self.prompt:
            raise ValueError(f"Prompt not set for agent {self.name}")

        messages = self.prompt.format_messages(**prompt_args)
        response = await self.llm.ainvoke(messages)
        return response.content

    def _add_message(self, state: GraphState, message: str) -> None:
        """Add a message to the state's message list with agent attribution.

        Args:
            state: The current state
            message: The message to add
        """
        state["messages"].append(f"[{self.name}] {message}")
        logger.info(f"[{self.name}] {message}")
