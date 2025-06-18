"""Optimization Advisor Agent for generating product improvement suggestions."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_app.agents.base_agent import BaseAgent
from langchain_app.workflow.state import GraphState
from langchain_app.core.logging_utils import configure_logger
from langchain_app.core.config import (
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    STATUS_SUCCESS,
    CATEGORY_PRODUCT_IMPROVEMENTS,
    CATEGORY_PRICING_STRATEGY,
    CATEGORY_CONTENT_OPTIMIZATION,
    CATEGORY_MARKETING_STRATEGY
)
from langchain_app.database.operations import (
    update_task_optimization_suggests,
    update_task_complete,
)

# Configure logger
logger = configure_logger(__name__)


class OptimizationAdvisorAgent(BaseAgent):
    """
    Agent responsible for generating product optimization suggestions.

    This agent:
    1. Analyzes market analysis results
    2. Identifies areas for product improvement
    3. Generates prioritized optimization suggestions
    """

    def __init__(self, model=DEFAULT_LLM_MODEL, temperature=DEFAULT_LLM_TEMPERATURE):
        """Initialize the optimization advisor agent."""
        super().__init__(
            "OptimizationAdvisorAgent", model=model, temperature=temperature
        )

        # Set up the optimization advisor prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
            You are a product optimization advisor. Based on the status and market analysis, generate:
            1. **Product Optimization Strategies** covering:
               • Title improvements  
               • Description enhancements  
               • Pricing adjustments  
               • Feature or packaging tweaks  
               • Any promotional or positioning tactics
            2. Prioritize recommendations by impact and ease of implementation.
            
            Please organize your suggestions into these categories:
            - {CATEGORY_PRODUCT_IMPROVEMENTS}: Physical product changes, features, packaging
            - {CATEGORY_PRICING_STRATEGY}: Price point adjustments, discounts, bundles
            - {CATEGORY_CONTENT_OPTIMIZATION}: Title, description, bullet points, images
            - {CATEGORY_MARKETING_STRATEGY}: Positioning, target audience, promotion
            
            Format your suggestions so they slot directly into the "Optimization Strategies" section of the report.
            """,
                ),
                (
                    "human",
                    "Generate optimization suggestions from analysis: {analysis}",
                ),
            ]
        )

    async def process(self, state: GraphState) -> GraphState:
        """Process optimization advisory tasks.

        Args:
            state: Current workflow state

        Returns:
            Updated state with optimization suggestions
        """
        self._add_message(state, "Starting optimization suggestions generation")

        # Verify we have the required data
        main_product = state.get("main_product")
        market_analysis = state.get("market_analysis")

        if not main_product:
            error_msg = "No main product available for optimization"
            state["error"] = error_msg
            self._add_message(state, error_msg)
            return state

        if not market_analysis:
            error_msg = "No market analysis available for optimization"
            state["error"] = error_msg
            self._add_message(state, error_msg)
            return state

        try:
            # Format the analysis data for the LLM
            # formatted_analysis = self._format_analysis_for_prompt(
            #     main_product, market_analysis
            # )

            # Generate optimization suggestions using the LLM
            self._add_message(
                state, f"Generating optimization suggestions for: {main_product.title}"
            )

            # Call the LLM with the formatted analysis
            analysis = {
                "main_product": main_product,
                "market_analysis": market_analysis,
            }
            prompt_args = {"analysis": analysis}
            llm_response = await self._run_llm(prompt_args)

            # Parse and structure the optimization suggestions
            # optimizations = self._structure_optimization_suggestions(llm_response)
            state["optimization_suggestions"] = llm_response

            # Update the task in the database with optimization suggestions
            db_task_id = state.get("db_task_id")
            if db_task_id:
                self._add_message(
                    state, f"Updating task {db_task_id} with optimization suggestions"
                )
                # Update optimization suggestions
                update_result = update_task_optimization_suggests(
                    db_task_id=db_task_id, optimization_suggests=llm_response
                )

                # Mark task as completed
                if update_result.get("status") == STATUS_SUCCESS:
                    complete_result = update_task_complete(
                        db_task_id=db_task_id, is_completed=True
                    )

                    if complete_result.get("status") != "success":
                        self._add_message(
                            state,
                            f"Failed to mark task as completed: {complete_result.get('error')}",
                        )
                if update_result.get("status") == "success":
                    self._add_message(
                        state,
                        "Task updated with optimization suggestions and marked as completed",
                    )
                else:
                    self._add_message(
                        state, f"Failed to update task: {update_result.get('error')}"
                    )
            else:
                self._add_message(
                    state,
                    "No task ID available, cannot update task with optimization suggestions",
                )

            # Add the full LLM response to state messages
            self._add_message(state, "## Product Optimization Suggestions")
            self._add_message(state, llm_response)

            self._add_message(state, "Optimization suggestions generation complete")
            return state

        except Exception as e:
            error_msg = f"Error during optimization suggestion generation: {str(e)}"
            state["error"] = error_msg
            self._add_message(state, error_msg)
            return state

    def _format_analysis_for_prompt(self, main_product, market_analysis):
        """Format the market analysis data for the LLM prompt.

        Args:
            main_product: The main product being optimized
            market_analysis: The market analysis data

        Returns:
            Formatted string containing analysis data for optimization
        """
        # Format the main product data
        product_info = {
            "title": main_product.title,
            "price": (
                main_product.price if hasattr(main_product, "price") else "Unknown"
            ),
            "description": (
                main_product.description
                if hasattr(main_product, "description")
                else "No description available"
            ),
            "features": (
                main_product.features
                if hasattr(main_product, "features")
                else ["No features listed"]
            ),
        }

        # Extract key information from market analysis
        analysis_summary = {
            "market_position": market_analysis.get("market_position", "Unknown"),
            "competitive_advantages": market_analysis.get("competitive_advantages", []),
            "competitive_disadvantages": market_analysis.get(
                "competitive_disadvantages", []
            ),
            "feature_gaps": market_analysis.get("feature_gaps", []),
            "price_positioning": market_analysis.get("price_positioning", {}),
            "positioning_recommendations": market_analysis.get(
                "positioning_recommendations", []
            ),
            "raw_analysis": market_analysis.get(
                "raw_analysis", "No raw analysis available"
            ),
        }

        # Combine product and analysis data
        formatted_data = {"product": product_info, "market_analysis": analysis_summary}

        return formatted_data

    def _structure_optimization_suggestions(self, llm_response):
        """Structure the LLM-generated optimization suggestions.

        Args:
            llm_response: Raw text from the LLM

        Returns:
            Dictionary of categorized optimization suggestions
        """
        # Extract categories and suggestions from the LLM response
        suggestions = {
            "Product Improvements": [],
            "Pricing Strategy": [],
            "Content Optimization": [],
            "Marketing Strategy": [],
        }

        # Parse the LLM output to extract suggestions by category
        current_category = None
        lines = llm_response.split("\n")

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check for category headers
            lower_line = line.lower()
            if "product" in lower_line and (
                "improvement" in lower_line or "feature" in lower_line
            ):
                current_category = "Product Improvements"
                continue
            elif "price" in lower_line or "pricing" in lower_line:
                current_category = "Pricing Strategy"
                continue
            elif (
                "title" in lower_line
                or "description" in lower_line
                or "content" in lower_line
            ) and not current_category:
                current_category = "Content Optimization"
                continue
            elif (
                "marketing" in lower_line
                or "promotion" in lower_line
                or "position" in lower_line
            ) and not current_category:
                current_category = "Marketing Strategy"
                continue

            # If we have a current category and this looks like a list item, add it
            if current_category and (
                line.startswith("-")
                or line.startswith("*")
                or line.startswith("•")
                or line.startswith("1.")
            ):
                item = line.lstrip("-*•123456789. ")
                if item:
                    # Add to the appropriate category
                    if current_category in suggestions:
                        suggestions[current_category].append(item)
                    else:
                        # If we find suggestions that don't match our predefined categories
                        # assign them to the most relevant category
                        if "feature" in item.lower() or "product" in item.lower():
                            suggestions["Product Improvements"].append(item)
                        elif "price" in item.lower() or "discount" in item.lower():
                            suggestions["Pricing Strategy"].append(item)
                        elif (
                            "title" in item.lower()
                            or "description" in item.lower()
                            or "image" in item.lower()
                        ):
                            suggestions["Content Optimization"].append(item)
                        else:
                            suggestions["Marketing Strategy"].append(item)

        # Ensure we have at least one suggestion in each category
        for category in suggestions:
            if not suggestions[category]:
                suggestions[category] = [
                    f"No specific {category.lower()} suggestions identified"
                ]
            else:
                # Limit to top 5 suggestions per category
                suggestions[category] = suggestions[category][:5]

        return suggestions
