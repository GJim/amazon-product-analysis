"""Models for the Amazon product analysis app."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

import sys
import os

# Add the parent directory to sys.path to import amazon_scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from amazon_scraper.models import ProductInfo


@dataclass
class Product:
    """Class to store product information with metadata."""

    url: str
    product_info: ProductInfo = field(default_factory=ProductInfo)
    collected_at: datetime = field(default_factory=datetime.now)
    is_main_product: bool = False
    similarity_score: float = 0.0

    @property
    def title(self) -> str:
        """Get the product title."""
        return self.product_info.title or "Unknown Title"

    @property
    def price(self) -> str:
        """Get the product price."""
        return self.product_info.price or "Unknown Price"

    @property
    def asin(self) -> str:
        """Get the product ASIN."""
        # Check if ASIN is in details specifications
        if self.product_info.details and "asin" in self.product_info.details.specifications:
            return self.product_info.details.specifications["asin"]
        return ""

    @property
    def description(self) -> str:
        """Get the product description."""
        return self.product_info.description or ""

    @property
    def similar_items_links(self) -> List[str]:
        """Get the similar items links."""
        return self.product_info.similar_items_links

    def __str__(self) -> str:
        """String representation of the product."""
        return f"Product(title={self.title}, price={self.price}, asin={self.asin})"
