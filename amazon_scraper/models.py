"""
Data models for Amazon product scraping.
These models define the structure of the data extracted from Amazon product pages.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Review(BaseModel):
    """Model representing a product review."""

    title: Optional[str] = None
    rating: Optional[str] = None
    text: Optional[str] = None
    reviewer: Optional[str] = None
    date: Optional[str] = None
    verified_purchase: bool = False


class ProductDetails(BaseModel):
    """Model representing product details/specifications."""

    availability: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    specifications: Dict[str, str] = Field(default_factory=dict)


class ProductInfo(BaseModel):
    """Model representing complete Amazon product information."""

    title: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    main_image_url: Optional[str] = None
    similar_items_links: List[str] = Field(default_factory=list)
    reviews: List[Review] = Field(default_factory=list)
    details: ProductDetails = Field(default_factory=ProductDetails)
