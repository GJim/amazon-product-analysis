"""
Celery tasks for database operations in Amazon Product Analysis.
"""

import logging
from typing import Dict, Any

from workers.celery_app import celery_app
from amazon_scraper.models import ProductInfo
from database.config import get_db_session
from database.utils import pydantic_to_sqlalchemy, sqlalchemy_to_pydantic

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@celery_app.task(name="workers.sinker.create_product")
def create_product(
    product_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Task to create a product in the database.

    Args:
        product_info: Dictionary representation of ProductInfo model

    Returns:
        Dict containing operation result and product ID
    """
    try:
        logger.info(f"Creating product record")
        
        # Convert dict to ProductInfo model
        product_data = ProductInfo(**product_info)
        
        # Get database session
        db = get_db_session()
        
        try:
            # Convert Pydantic model to SQLAlchemy model
            db_product = pydantic_to_sqlalchemy(product_data, db)
            
            # Add to session if new
            db.add(db_product)
                
            # Commit changes
            db.commit()
            db.refresh(db_product)
            
            # Convert back to Pydantic model to verify data integrity
            saved_product = sqlalchemy_to_pydantic(db_product)
            
            logger.info(f"Successfully created product with ID: {db_product.id}")
            return {
                "status": "success", 
                "product_id": db_product.id,
                "operation": "create"
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to create product: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }
