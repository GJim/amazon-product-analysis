from .scraper import extract_product_info
from .models import ProductInfo, ProductDetails, Review

__all__ = [
    "extract_product_info",  # Main parsing function
    "ProductInfo",  # Main product data model
    "ProductDetails",  # Product details model
    "Review",  # Review model
]
__version__ = "0.1.0"
