from .scraper import extract_product_info, scrape_product_info
from .models import ProductInfo, ProductDetails, Review
from . import config

__all__ = [
    "extract_product_info",  # Main parsing function
    "scrape_product_info",   # Main scraping function
    "ProductInfo",          # Main product data model
    "ProductDetails",       # Product details model
    "Review",               # Review model
    "config",               # Configuration module
]
__version__ = "0.1.0"
