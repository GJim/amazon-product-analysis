"""
Database configuration for SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from database.models import Base

db_username: str = os.environ.get("DB_USERNAME", "postgres")
db_password: str = os.environ.get("DB_PASSWORD", "postgres")
db_host: str = os.environ.get("DB_HOST", "localhost")
db_port: int = int(os.environ.get("DB_PORT", 5432))
db_name: str = os.environ.get("DB_NAME", "amazon_product_analysis")

database_url = (
    f"postgresql+psycopg://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
)
print(database_url)

# Create SQLAlchemy engine
engine = create_engine(database_url)

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
