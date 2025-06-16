# Amazon Product Analysis - Architecture

## Project Purpose

The Amazon Product Analysis project is designed to provide competitive market analysis for Amazon products. It helps users gain insights into product positioning, market opportunities, and optimization suggestions by:

1. **Analyzing Amazon Products**: Retrieving and analyzing data from Amazon product pages including titles, prices, descriptions, reviews, and more.
2. **Competitive Analysis**: Comparing target products with similar/competitive products to identify market positioning.
3. **Optimization Suggestions**: Providing data-driven suggestions to improve product listings and marketing strategies.

## Technical Stack Architecture

The project follows a modular architecture with several key components:

### 1. Data Collection Layer
- **Amazon Scraper**: A Python library that handles the extraction of product data from Amazon pages
  - Handles CAPTCHA challenges via Anti-CAPTCHA integration
  - Extracts product details, images, reviews, and similar product links
- **Browser Automation**: Uses browser automation to navigate Amazon and extract information

### 2. Data Storage Layer
- **PostgreSQL Database**: Stores all product data and analysis results
  - Structured tables for products, reviews, details, and analysis tasks
  - Supports JSON data for flexible storage of product specifications

### 3. Processing Layer
- **Celery Task Queue**: Manages asynchronous processing of analysis requests
  - Handles background scraping and analysis tasks
  - Provides task status tracking

### 4. Backend API Layer
- **FastAPI Application**: Provides RESTful API endpoints
  - Endpoints for submitting analysis requests
  - Task status monitoring endpoints
  - WebSocket support for real-time updates

### 5. Integration Components
- **Redis**: Used as message broker for Celery tasks and WebSocket management
- **WebSocket Service**: Provides real-time updates on task progress

## Data Flow

1. Client submits an Amazon product URL through the API
2. Backend creates an analysis task and adds it to the Celery queue
3. Worker processes:
   - Scrape the target product data
   - Identify and scrape competitive products
   - Perform market analysis
   - Store results in the database
4. Client receives updates through WebSockets or by polling the task status endpoint

## Deployment Architecture

The system is designed to be deployed as a set of services:
- Database service (PostgreSQL)
- Redis service (for message brokering)
- API service (FastAPI)
- Worker service (Celery)

Each component can be scaled independently based on load requirements.
