"""
Database configuration for SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from database.models import Base

# Get database URL from environment variables or use a default
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@localhost:5432/amazon_product_analysis"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Function to get a database session
def get_db_session():
    """Get a new database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Function to initialize database
def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


# Function to get a database session as a context manager
def get_db():
    """Get a database session as a context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
