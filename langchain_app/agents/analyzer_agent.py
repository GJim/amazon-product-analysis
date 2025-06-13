"""Market Analyzer Agent for market positioning and competitive analysis."""

import logging
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
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
    Agent responsible for analyzing market positioning and competitive landscape.

    This agent:
    1. Analyzes the main product's features, price, and benefits
    2. Compares with competitive products
    3. Identifies market positioning
    4. Determines competitive advantages and disadvantages
    """

    def __init__(self, model="gpt-4o", temperature=0):
        """Initialize the market analyzer agent."""
        super().__init__("MarketAnalyzerAgent", model=model, temperature=temperature)

        # Set up the market analyzer prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            You are a market analysis specialist. From the collected data, produce:
            1. **Competitive Product Analysis**:
               • A side-by-side strengths & weaknesses comparison between main product and each competitor.
            2. **Market Positioning Recommendations**:
               • Where the main product sits in the market (e.g., premium vs. budget).
               • Suggested positioning angles to exploit gaps.
            3. Any notable **price positioning** or **feature gaps**.
            Frame your output so it can slot directly into the report under "Competitive Analysis" and "Market Positioning."
            """,
                ),
                ("human", "Analyze market and competitor data: {data}"),
            ]
        )

    async def process(self, state: GraphState) -> GraphState:
        """Process market analysis tasks.

        Args:
            state: Current workflow state

        Returns:
            Updated state with market analysis
        """
        self._add_message(state, "Starting market analysis")

        # Verify we have the required data
        main_product = state.get("main_product")
        competitive_products = state.get("competitive_products", [])

        if not main_product:
            error_msg = "No main product available for analysis"
            state["error"] = error_msg
            self._add_message(state, error_msg)
            return state

        if not competitive_products:
            error_msg = "No competitive products available for analysis"
            state["error"] = error_msg
            self._add_message(state, error_msg)
            return state

        # Perform analysis
        self._add_message(state, f"Analyzing main product: {main_product.title}")
        self._add_message(
            state, f"Comparing with {len(competitive_products)} competitive products"
        )

        try:
            # Format product data for the LLM
            formatted_data = self._format_product_data_for_prompt(
                main_product, competitive_products
            )

            # Send data to LLM for analysis
            prompt_args = {"data": formatted_data}
            llm_analysis = await self._run_llm(prompt_args)

            # Parse and structure the analysis
            # analysis_result = self._structure_analysis_result(llm_analysis)
            state["market_analysis"] = llm_analysis

            # Add the analysis to messages
            self._add_message(state, "## Market Analysis Results")
            self._add_message(state, llm_analysis)

            return state

        except Exception as e:
            error_msg = f"Error during market analysis: {str(e)}"
            state["error"] = error_msg
            self._add_message(state, error_msg)
            return state

    def _format_product_data_for_prompt(self, main_product, competitive_products):
        """Format product data for the LLM prompt.

        Args:
            main_product: The main product being analyzed
            competitive_products: List of competitive products for comparison

        Returns:
            Formatted string containing product data for analysis
        """
        # Format the main product data
        # main_product_info = {
        #     "title": main_product.title,
        #     "price": (
        #         main_product.price if hasattr(main_product, "price") else "Unknown"
        #     ),
        #     "rating": (
        #         main_product.rating if hasattr(main_product, "rating") else "Unknown"
        #     ),
        #     "features": (
        #         main_product.features[:5]
        #         if hasattr(main_product, "features") and main_product.features
        #         else ["No features listed"]
        #     ),
        #     "description": (
        #         main_product.description
        #         if hasattr(main_product, "description")
        #         else "No description available"
        #     ),
        # }

        # Format the competitive products data
        # competitive_products_info = []
        # for i, product in enumerate(
        #     competitive_products[:5]
        # ):  # Limit to top 5 competitors
        #     product_info = {
        #         "title": product.title,
        #         "price": product.price if hasattr(product, "price") else "Unknown",
        #         "rating": product.rating if hasattr(product, "rating") else "Unknown",
        #         "features": (
        #             product.features[:3]
        #             if hasattr(product, "features") and product.features
        #             else ["No features listed"]
        #         ),
        #     }
        #     competitive_products_info.append(product_info)

        # Create a structured format for the LLM
        formatted_data = {
            "main_product": main_product,
            "competitive_products": competitive_products,
            "total_competitors": len(competitive_products),
        }

        return formatted_data

    def _structure_analysis_result(self, llm_analysis):
        """Structure the LLM analysis result into a standardized format.

        Args:
            llm_analysis: The raw analysis text from the LLM

        Returns:
            Dictionary containing structured analysis results
        """
        # This is a simple implementation - in production, you might want to parse the LLM output
        # more carefully or have the LLM output structured JSON
        analysis = {
            "raw_analysis": llm_analysis,
            "market_position": self._extract_market_position(llm_analysis),
            "competitive_advantages": self._extract_list_items(
                llm_analysis, "strengths", "advantages"
            ),
            "competitive_disadvantages": self._extract_list_items(
                llm_analysis, "weaknesses", "disadvantages"
            ),
            "price_positioning": self._extract_price_positioning(llm_analysis),
            "feature_gaps": self._extract_list_items(
                llm_analysis, "feature gaps", "missing features"
            ),
            "positioning_recommendations": self._extract_list_items(
                llm_analysis, "positioning", "recommendations"
            ),
        }

        return analysis

    def _extract_market_position(self, text):
        """Extract market position from analysis text.

        Args:
            text: Analysis text from LLM

        Returns:
            Extracted market position or default value
        """
        position_keywords = [
            "premium",
            "luxury",
            "mid-range",
            "budget",
            "value",
            "economy",
            "high-end",
        ]
        for keyword in position_keywords:
            if keyword in text.lower():
                return keyword
        return "mid-range"  # Default if no position is detected

    def _extract_price_positioning(self, text):
        """Extract price positioning information from analysis text.

        Args:
            text: Analysis text from LLM

        Returns:
            Dictionary with price positioning information
        """
        # Simple extraction - in production this could be more sophisticated
        positioning_info = {}

        # Check for common price positioning phrases
        if "higher price" in text.lower() or "more expensive" in text.lower():
            positioning_info["relative_position"] = "above average"
        elif "lower price" in text.lower() or "less expensive" in text.lower():
            positioning_info["relative_position"] = "below average"
        else:
            positioning_info["relative_position"] = "average"

        # Extract a snippet about pricing
        positioning_info["price_analysis"] = self._extract_section(text, "price", 200)

        return positioning_info

    def _extract_list_items(self, text, *keywords):
        """Extract list items related to keywords from text.

        Args:
            text: Text to extract items from
            keywords: Keywords to look for when extracting items

        Returns:
            List of extracted items
        """
        items = []
        lines = text.split("\n")

        # Look for lines that start with a list marker and contain any of the keywords
        capture = False
        for line in lines:
            line = line.strip()

            # Check if the line has any of our keywords
            if any(keyword.lower() in line.lower() for keyword in keywords):
                capture = True

            # If we're capturing and the line starts with a list marker, add it
            if capture and (
                line.startswith("-") or line.startswith("•") or line.startswith("*")
            ):
                # Clean up the line
                item = line.lstrip("-•* ").strip()
                if item and len(item) > 5:  # Only add substantive items
                    items.append(item)

            # Stop capturing if we hit a header or empty line after capturing some items
            if capture and items and (not line or line.startswith("#")):
                capture = False

        # If we don't find any items, return placeholder items
        if not items:
            items = [f"No clear {'/'.join(keywords)} identified in the analysis"]

        return items[:5]  # Limit to 5 items

    def _extract_section(self, text, keyword, max_chars=200):
        """Extract a section of text around a keyword.

        Args:
            text: Text to extract section from
            keyword: Keyword to center the extraction around
            max_chars: Maximum number of characters to extract

        Returns:
            Extracted section
        """
        keyword_pos = text.lower().find(keyword.lower())
        if keyword_pos == -1:
            return f"No information about {keyword} found"

        # Extract text around the keyword
        start = max(0, keyword_pos - max_chars // 2)
        end = min(len(text), keyword_pos + max_chars // 2)

        # Adjust to avoid cutting words
        while start > 0 and text[start] != " ":
            start -= 1

        while end < len(text) - 1 and text[end] != " ":
            end += 1

        return text[start:end].strip()

    def _analyze_market(
        self, main_product: Product, competitive_products: List[Product]
    ) -> Dict[str, Any]:
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
                price_str = product.price.replace("$", "").replace(",", "")
                price = float(price_str)
                competitor_prices.append(price)
            except (ValueError, AttributeError):
                # Skip products with unparseable prices
                pass

        avg_competitor_price = (
            sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0
        )

        # Determine main product price
        main_price = 0
        try:
            price_str = main_product.price.replace("$", "").replace(",", "")
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
        if (
            main_product.product_info.details
            and main_product.product_info.details.specifications
        ):
            main_features = list(
                main_product.product_info.details.specifications.keys()
            )

        # Identify common and distinguishing features
        all_competitor_features = []
        for product in competitive_products:
            if (
                product.product_info.details
                and product.product_info.details.specifications
            ):
                all_competitor_features.extend(
                    list(product.product_info.details.specifications.keys())
                )

        # Count feature frequency
        feature_frequency = {}
        for feature in all_competitor_features:
            feature_frequency[feature] = feature_frequency.get(feature, 0) + 1

        # Identify distinguishing features of main product
        distinguishing_features = []
        for feature in main_features:
            if (
                feature not in feature_frequency
                or feature_frequency[feature] < len(competitive_products) / 2
            ):
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
            competitive_advantages.append(
                "Premium pricing suggests higher quality perception"
            )
            competitive_disadvantages.append(
                "Higher price point may deter budget-conscious customers"
            )
        elif price_position == "budget":
            competitive_advantages.append(
                "Lower price point may attract cost-conscious customers"
            )
            competitive_disadvantages.append(
                "Lower price may signal lower quality to some customers"
            )

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
            "analyzed_competitors": len(competitive_products),
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
            f"- Analyzed {analysis.get('analyzed_competitors', 0)} competitive products",
        ]

        # Add price analysis
        summary.append("\n### Price Analysis")
        summary.append(
            f"- Main Product Price: ${analysis.get('main_product_price', 0):.2f}"
        )
        summary.append(
            f"- Average Competitor Price: ${analysis.get('avg_competitor_price', 0):.2f}"
        )

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
