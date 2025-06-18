"""
Direct database operations for the LangChain app.

This module provides functions for direct database operations without using Celery tasks.
It's intended for operations that need to be synchronous within the workflow.
"""

import uuid
from typing import Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from langchain_app.core.logging_utils import configure_logger
from langchain_app.core.config import (
    MAX_PRODUCT_LIMIT_DB,
    MAX_COMPETITIVE_LIMIT_DB,
    STATUS_SUCCESS,
    STATUS_ERROR
)

from database.models import (
    Task,
    MainProduct,
    CompetitiveProduct,
    Product,
    Review,
    ProductDetail,
)
from database.config import get_db_session
from amazon_scraper.models import ProductInfo

# Configure logger
logger = configure_logger(__name__)


def create_task_record(
    url: str,
    max_product: int = MAX_PRODUCT_LIMIT_DB,
    max_competitive: int = MAX_COMPETITIVE_LIMIT_DB,
) -> Dict[str, Any]:
    """
    Create a task record in the database.

    Args:
        url: The Amazon product URL
        max_product: Maximum number of products to collect
        max_competitive: Maximum number of competitive products to analyze

    Returns:
        Dict containing operation result and task UUID
    """
    try:
        db = get_db_session()

        # Generate UUID for the task
        task_uuid = str(uuid.uuid4())

        # Create task record
        task = Task(
            uuid=task_uuid,
            url=url,
            max_product=max_product,
            max_competitive=max_competitive,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Created task record with UUID: {task_uuid} and ID: {task.id}")

        return {
            "status": "success",
            "message": "Task created successfully",
            "db_task_id": task.id,
        }

    except SQLAlchemyError as e:
        db.rollback()
        error_message = f"Database error creating task: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    except Exception as e:
        db.rollback()
        error_message = f"Error creating task: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    finally:
        db.close()


def create_product_record(product_info: ProductInfo) -> Dict[str, Any]:
    """
    Create a product record in the database.

    Args:
        product_info: ProductInfo model

    Returns:
        Dict containing operation result and product ID
    """
    try:
        db = get_db_session()

        # Convert ProductInfo to ProductDetail
        product_detail = ProductDetail(
            availability=product_info.details.availability,
            categories=product_info.details.categories,
            specifications=product_info.details.specifications,
        )

        # Convert ProductInfo to Review
        reviews = [
            Review(
                title=review.title,
                rating=review.rating,
                text=review.text,
                reviewer=review.reviewer,
                date=review.date,
                verified_purchase=review.verified_purchase,
            )
            for review in product_info.reviews
        ]

        # Convert dict to Product model
        product = Product(
            title=product_info.title,
            price=product_info.price,
            description=product_info.description,
            main_image_url=product_info.main_image_url,
            similar_items_links=product_info.similar_items_links,
            reviews=reviews,
            details=product_detail,
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        logger.info(f"Created product record with ID: {product.id}")

        return {
            "status": "success",
            "message": "Product created successfully",
            "product_id": product.id,
        }

    except SQLAlchemyError as e:
        db.rollback()
        error_message = f"Database error creating product: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    except Exception as e:
        db.rollback()
        error_message = f"Error creating product: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    finally:
        db.close()


def create_main_product_record(db_task_id: int, product_id: int) -> Dict[str, Any]:
    """
    Create a main product record linking a task to a product.

    Args:
        db_task_id: The task ID
        product_id: The product ID to link as main product

    Returns:
        Dict containing operation result and main product ID
    """
    try:
        db = get_db_session()

        # Create main product link
        main_product = MainProduct(task_id=db_task_id, product_id=product_id)

        db.add(main_product)
        db.commit()
        db.refresh(main_product)

        logger.info(f"Created main product link with ID: {main_product.id}")

        return {
            "status": "success",
            "message": "Main product link created successfully",
            "main_product_id": main_product.id,
        }

    except SQLAlchemyError as e:
        db.rollback()
        error_message = f"Database error creating main product link: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    except Exception as e:
        db.rollback()
        error_message = f"Error creating main product link: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    finally:
        db.close()


def create_competitive_product_record(
    db_task_id: int, main_product_id: int, product_id: int
) -> Dict[str, Any]:
    """
    Create a competitive product record linking a product to a task and main product.

    Args:
        db_task_id: The task ID
        main_product_id: The main product ID
        product_id: The product ID to link as competitive product

    Returns:
        Dict containing operation result and competitive product ID
    """
    try:
        db = get_db_session()

        # Create competitive product link
        competitive_product = CompetitiveProduct(
            task_id=db_task_id, main_product_id=main_product_id, product_id=product_id
        )

        db.add(competitive_product)
        db.commit()
        db.refresh(competitive_product)

        logger.info(
            f"Created competitive product link with ID: {competitive_product.id}"
        )

        return {
            "status": "success",
            "message": "Competitive product link created successfully",
            "competitive_product_id": competitive_product.id,
        }

    except SQLAlchemyError as e:
        db.rollback()
        error_message = f"Database error creating competitive product link: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    except Exception as e:
        db.rollback()
        error_message = f"Error creating competitive product link: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    finally:
        db.close()


def update_task_market_analysis(
    db_task_id: int, market_analysis: str
) -> Dict[str, Any]:
    """
    Update a task's market analysis.

    Args:
        db_task_id: The task ID
        market_analysis: The market analysis text

    Returns:
        Dict containing operation result
    """
    try:
        db = get_db_session()

        # Find the task by ID
        task = db.query(Task).filter(Task.id == db_task_id).first()
        if not task:
            return {"status": "error", "error": f"Task with ID {db_task_id} not found"}

        # Update the market analysis
        task.market_analysis = market_analysis

        db.commit()

        logger.info(f"Updated market analysis for task with ID: {db_task_id}")

        return {"status": "success", "message": "Market analysis updated successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        error_message = f"Database error updating market analysis: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    except Exception as e:
        db.rollback()
        error_message = f"Error updating market analysis: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    finally:
        db.close()


def update_task_optimization_suggests(
    db_task_id: int, optimization_suggests: str
) -> Dict[str, Any]:
    """
    Update a task's optimization suggestions.

    Args:
        db_task_id: The task ID
        optimization_suggests: The optimization suggestions text

    Returns:
        Dict containing operation result
    """
    try:
        db = get_db_session()

        # Find the task by ID
        task = db.query(Task).filter(Task.id == db_task_id).first()
        if not task:
            return {"status": "error", "error": f"Task with ID {db_task_id} not found"}

        # Update the optimization suggestions
        task.optimization_suggests = optimization_suggests

        db.commit()

        logger.info(f"Updated optimization suggestions for task with ID: {db_task_id}")

        return {
            "status": "success",
            "message": "Optimization suggestions updated successfully",
        }

    except SQLAlchemyError as e:
        db.rollback()
        error_message = f"Database error updating optimization suggestions: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    except Exception as e:
        db.rollback()
        error_message = f"Error updating optimization suggestions: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    finally:
        db.close()


def update_task_complete(db_task_id: int, is_completed: bool = True) -> Dict[str, Any]:
    """
    Mark a task as completed or not completed.

    Args:
        db_task_id: The task ID
        is_completed: Whether the task is completed

    Returns:
        Dict containing operation result
    """
    try:
        db = get_db_session()

        # Find the task by ID
        task = db.query(Task).filter(Task.id == db_task_id).first()
        if not task:
            return {"status": "error", "error": f"Task with ID {db_task_id} not found"}

        # Update the completion status
        task.is_completed = is_completed

        db.commit()

        logger.info(
            f"Updated completion status to {is_completed} for task with ID: {db_task_id}"
        )

        return {
            "status": "success",
            "message": f"Task {'completed' if is_completed else 'marked as incomplete'} successfully",
        }

    except SQLAlchemyError as e:
        db.rollback()
        error_message = f"Database error updating task completion status: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    except Exception as e:
        db.rollback()
        error_message = f"Error updating task completion status: {str(e)}"
        logger.error(error_message)
        return {"status": "error", "error": error_message}

    finally:
        db.close()
