"""
SQLAlchemy database models for Amazon product analysis.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
import uuid as uuid_lib

Base = declarative_base()


class Product(Base):
    """SQLAlchemy model for Amazon products."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=True)
    price = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    main_image_url = Column(String(1000), nullable=True)
    similar_items_links = Column(ARRAY(String), nullable=True, default=[])

    # Relationships
    reviews = relationship(
        "Review", back_populates="product", cascade="all, delete-orphan"
    )
    details = relationship(
        "ProductDetail",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title if self.title else 'None'}'>"


class Review(Base):
    """SQLAlchemy model for product reviews."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    title = Column(String(300), nullable=True)
    rating = Column(String(50), nullable=True)
    text = Column(Text, nullable=True)
    reviewer = Column(String(200), nullable=True)
    date = Column(String(50), nullable=True)
    verified_purchase = Column(Boolean, default=False)

    # Relationship
    product = relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, title='{self.title if self.title else 'None'}'>"


class ProductDetail(Base):
    """SQLAlchemy model for product details/specifications."""

    __tablename__ = "product_details"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    availability = Column(String(300), nullable=True)
    categories = Column(ARRAY(String), nullable=True, default=[])
    specifications = Column(JSONB, nullable=True, default={})

    # Relationship
    product = relationship("Product", back_populates="details")

    def __repr__(self):
        return f"<ProductDetail(id={self.id}, product_id={self.product_id})>"


class Task(Base):
    """SQLAlchemy model for analysis tasks."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid_lib.uuid4()))
    url = Column(String(1000), nullable=True)
    market_analysis = Column(Text, nullable=True)
    optimization_suggests = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    max_product = Column(Integer, default=0)
    max_competitive = Column(Integer, default=0)

    # Relationships
    main_products = relationship(
        "MainProduct", back_populates="task", cascade="all, delete-orphan"
    )
    competitive_products = relationship(
        "CompetitiveProduct", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, uuid='{self.uuid}', is_completed={self.is_completed})>"


class MainProduct(Base):
    """SQLAlchemy model for main products."""

    __tablename__ = "main_products"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    task = relationship("Task", back_populates="main_products")
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<MainProduct(id={self.id}, task_id={self.task_id}, product_id={self.product_id})>"


class CompetitiveProduct(Base):
    """SQLAlchemy model for competitive products."""

    __tablename__ = "competitive_products"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    main_product_id = Column(Integer, ForeignKey("products.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    task = relationship("Task", back_populates="competitive_products")
    main_product = relationship("Product", foreign_keys=[main_product_id])
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<CompetitiveProduct(id={self.id}, task_id={self.task_id}, product_id={self.product_id})>"
