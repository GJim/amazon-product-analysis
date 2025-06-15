"""
Utilities for working with database models and Pydantic models.
"""

from typing import Optional, Dict, Any, Union
from sqlalchemy.orm import Session

from amazon_scraper.models import ProductInfo, Review as PydanticReview, ProductDetails as PydanticProductDetails
from database.models import Product, Review, ProductDetail


def pydantic_to_sqlalchemy(product_info: ProductInfo, db: Session, existing_product: Optional[Product] = None) -> Product:
    """
    Convert a Pydantic ProductInfo model to SQLAlchemy Product model.
    If existing_product is provided, it will update that instance.
    
    Args:
        product_info: Pydantic ProductInfo model
        db: SQLAlchemy database session
        existing_product: Optional existing Product to update
        
    Returns:
        SQLAlchemy Product instance
    """
    if existing_product:
        product = existing_product
    else:
        product = Product()
    
    # Update basic product attributes
    product.title = product_info.title
    product.price = product_info.price
    product.description = product_info.description
    product.main_image_url = product_info.main_image_url
    product.similar_items_links = product_info.similar_items_links if product_info.similar_items_links else []
    
    # Handle product details
    if existing_product and existing_product.details:
        product_details = existing_product.details
    else:
        product_details = ProductDetail()
        product_details.product = product
        
    product_details.availability = product_info.details.availability
    product_details.categories = product_info.details.categories if product_info.details.categories else []
    product_details.specifications = product_info.details.specifications if product_info.details.specifications else {}
    
    # Handle reviews
    if product_info.reviews:            
        # Add new reviews
        for pydantic_review in product_info.reviews:
            review = Review()
            review.title = pydantic_review.title
            review.rating = pydantic_review.rating
            review.text = pydantic_review.text
            review.reviewer = pydantic_review.reviewer
            review.date = pydantic_review.date
            review.verified_purchase = pydantic_review.verified_purchase
            review.product = product
    
    return product


def sqlalchemy_to_pydantic(product: Product) -> ProductInfo:
    """
    Convert SQLAlchemy Product model to Pydantic ProductInfo model.
    
    Args:
        product: SQLAlchemy Product instance
        
    Returns:
        Pydantic ProductInfo model
    """
    # Convert reviews
    reviews = []
    if product.reviews:
        for review in product.reviews:
            reviews.append(PydanticReview(
                title=review.title,
                rating=review.rating,
                text=review.text,
                reviewer=review.reviewer,
                date=review.date,
                verified_purchase=review.verified_purchase
            ))
    
    # Convert product details
    details = PydanticProductDetails()
    if product.details:
        details = PydanticProductDetails(
            availability=product.details.availability,
            categories=product.details.categories if product.details.categories else [],
            specifications=product.details.specifications if product.details.specifications else {}
        )
    
    # Create ProductInfo
    return ProductInfo(
        title=product.title,
        price=product.price,
        description=product.description,
        main_image_url=product.main_image_url,
        similar_items_links=product.similar_items_links if product.similar_items_links else [],
        reviews=reviews,
        details=details
    )
