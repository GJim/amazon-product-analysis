"""Base agent class for Amazon product analysis agents."""

import os
import json
import datetime
from typing import Any, Dict, List, Optional
import redis

from langchain_app.core.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    REDIS_CHANNEL_PREFIX,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE
)
from langchain_app.core.logging_utils import configure_logger

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langchain_app.workflow.state import GraphState

# Configure logger
logger = configure_logger(__name__)


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, name: str, model: str = DEFAULT_LLM_MODEL, temperature: float = DEFAULT_LLM_TEMPERATURE):
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
        formatted_message = f"[{self.name}] {message}"
        state["messages"].append(formatted_message)
        logger.info(formatted_message)
        
        # Publish message to Redis if task_id is available
        task_id = state.get("task_id")

        if task_id:
            try:
                # Connect to Redis
                redis_client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD
                )
                
                # Create channel name with prefix as requested
                channel_name = f"{REDIS_CHANNEL_PREFIX}_{task_id}"
                
                # Create message payload
                payload = {
                    "agent": self.name,
                    "message": message,
                    "timestamp": str(datetime.datetime.now())
                }
                
                # Publish JSON message to the channel
                redis_client.publish(channel_name, json.dumps(payload))
                logger.debug(f"Published message to Redis channel: {channel_name}")
            except Exception as e:
                logger.error(f"Failed to publish message to Redis: {str(e)}")
                # Don't raise the exception - we don't want to break the workflow if Redis fails
