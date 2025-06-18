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

- Docker and Docker Compose
- OpenAI API Key (for product analysis features)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GJim/amazon-product-analysis.git
   cd amazon-product-analysis
   ```

2. **Build and start the services:**
   ```bash
   chmod +x docker-compose-run.sh
   ./docker-compose-run.sh
   ```

## Usage

### Accessing the Service

- **Frontend Interface**: http://localhost:80
- **API Documentation**: http://localhost:8000/docs

### Managing the Service

- **View logs from a specific service:**
  ```bash
  docker-compose logs -f backend  # Replace 'backend' with any service name
  ```

- **Stop all services:**
  ```bash
  docker-compose down
  ```

- **Restart a specific service:**
  ```bash
  docker-compose restart backend  # Replace 'backend' with any service name
  ```

## Development & Testing

### Running Tests in Docker

```bash
# Run all tests
docker-compose exec backend python -m unittest discover tests

# Run specific components
docker-compose exec backend python -m unittest tests/test_amazon_scraper.py  # Test the scraper
```

### Local Development

For local development without Docker:

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure local environment variables** by copying values from your `.env` file.

## Documentation

For more detailed information about the project, refer to:

- [Architecture Documentation](ARCHITECTURE.md) - Project structure and technical stack
- [API Documentation](API.md) - Details on backend endpoints and their usage

## Troubleshooting

### Common Issues

1. **Docker Container Issues**
   - Check container status: `docker-compose ps`
   - View container logs: `docker-compose logs -f <service_name>`
   - Restart services: `docker-compose restart <service_name>`

2. **Database Connection Issues**
   - Verify the PostgreSQL container is running: `docker-compose ps postgres`
   - Check PostgreSQL logs: `docker-compose logs -f postgres`
   - Ensure environment variables in `.env` match those in `docker-compose.yml`

3. **Celery Worker Issues**
   - Check worker logs: `docker-compose logs -f worker`
   - Verify Redis connection: `docker-compose logs -f redis`

4. **Amazon Scraping Issues**
   - Amazon might block requests - use proper headers and respect rate limits
   - Current method to handle CAPTCHA issues may become invalid

## Disclaimer

- Web scraping Amazon's website may be against their Terms of Service. Use this system responsibly and at your own risk.
- Amazon's website structure changes frequently, which may break the scraper. The selectors might need updates over time.
- This project is for educational and research purposes only.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
