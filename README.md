# Amazon Product Analysis

A complete system for analyzing Amazon products, comparing them with competitive offerings, and providing optimization suggestions. The system combines web scraping, asynchronous processing, and data analysis to deliver comprehensive market insights.

## Features

- **Product Data Extraction**: Fetch product title, price, description, images, and specifications from Amazon.
- **Competitive Analysis**: Automatically identify and analyze similar products for market comparison.
- **Market Insights**: Generate data-driven market analysis for Amazon product listings.
- **Optimization Suggestions**: Receive optimization suggestions based on analysis results.
- **Real-time Updates**: Track analysis progress through WebSockets.
- **REST API**: Programmatically interact with the analysis system.
- **CAPTCHA Handling**: Built-in solution for handling Amazon's anti-bot measures.

## Prerequisites

- Python 3.10+
- PostgreSQL 17+
- Redis (for message broker)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GJim/amazon-product-analysis.git
   cd amazon-product-analysis
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```bash
   # install postgresql
   docker run -d --name postgres -e POSTGRES_PASSWORD=<your_password> -p 5432:5432 postgres:17

   # Create database and initial tables
   psql -U postgres -f database/00_init.sql
   
   # Initialize database schema
   python setup_database.py
   ```

5. **Configure environment:**
   Create a `.env` file in the root directory with the following variables:
   ```bash
   mv .env.example .env
   ```

## Usage

### Running the Service

1. **Start Redis:**
   ```bash
   docker run -d --name redis -p 6379:6379 redis
   ```

2. **Start Celery workers:**
   ```bash
   # From the project root directory
   celery -A workers.celery_app worker --loglevel=info --concurrency=1 --queues=analysis_agent
   ```

3. **Start the FastAPI backend:**
   ```bash
   # From the project root directory
   python -m backend.run_backend
   ```
   The API will be available at http://localhost:8000

## Development & Testing

### Running Tests
```bash
# Run all tests
python -m unittest discover tests

# Run specific components
python -m unittest tests/test_amazon_scraper.py  # Test the scraper
```

## Documentation

For more detailed information about the project, refer to:

- [Architecture Documentation](ARCHITECTURE.md) - Project structure and technical stack
- [API Documentation](API.md) - Details on backend endpoints and their usage

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running and the connection string is correct
   - Ensure database permissions are set correctly

2. **Celery Worker Issues**
   - Check if Redis is running
   - Verify Celery worker logs for errors

3. **Amazon Scraping Issues**
   - Amazon might block requests - use proper headers and respect rate limits
   - Current method to handle CAPTCHA issues become invalid

## Disclaimer

- Web scraping Amazon's website may be against their Terms of Service. Use this system responsibly and at your own risk.
- Amazon's website structure changes frequently, which may break the scraper. The selectors might need updates over time.
- This project is for educational and research purposes only.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
