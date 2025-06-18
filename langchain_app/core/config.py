"""Configuration settings for the Amazon product analysis application."""

import os

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")  # Set this via environment variable
REDIS_CHANNEL_PREFIX = os.getenv("REDIS_CHANNEL_PREFIX", "product_analysis")

# LLM configuration
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o")
DEFAULT_LLM_TEMPERATURE = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0"))

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Database limits
MAX_PRODUCTS_TO_ANALYZE = int(os.getenv("MAX_PRODUCTS_TO_ANALYZE", "5"))
MAX_REVIEWS_PER_PRODUCT = int(os.getenv("MAX_REVIEWS_PER_PRODUCT", "20"))
MAX_PRODUCT_LIMIT_DB = int(os.getenv("MAX_PRODUCT_LIMIT_DB", "10"))
MAX_COMPETITIVE_LIMIT_DB = int(os.getenv("MAX_COMPETITIVE_LIMIT_DB", "5"))
MAX_SCRAPE_ATTEMPTS = int(os.getenv("MAX_SCRAPE_ATTEMPTS", "20"))

# Status codes
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"

# Workflow control
WORKFLOW_END = "END"

# Analysis settings
POSITION_ABOVE_AVERAGE = "above average"
POSITION_BELOW_AVERAGE = "below average"
POSITION_AVERAGE = "average"
POSITION_UNKNOWN = "unknown"

PRICE_POSITION_PREMIUM = "premium"
PRICE_POSITION_BUDGET = "budget"
PRICE_POSITION_MID_RANGE = "mid-range"
PRICE_POSITION_UNKNOWN = "unknown"

EXTRACT_MAX_CHARS = 200

# Report categories
CATEGORY_PRODUCT_IMPROVEMENTS = "Product Improvements"
CATEGORY_PRICING_STRATEGY = "Pricing Strategy"
CATEGORY_CONTENT_OPTIMIZATION = "Content Optimization"
CATEGORY_MARKETING_STRATEGY = "Marketing Strategy"

# Report formatting
REPORT_BORDER = "=" * 80
REPORT_SECTION_BORDER = "-" * 80
REPORT_MAIN_PRODUCT_HEADER = "📦 MAIN PRODUCT INFORMATION"
REPORT_MARKET_ANALYSIS_HEADER = "📊 MARKET ANALYSIS"
REPORT_OPTIMIZATION_HEADER = "🚀 OPTIMIZATION SUGGESTIONS"
REPORT_COMPETITIVE_PRODUCTS_HEADER = "🏆 COMPETITIVE PRODUCTS"
