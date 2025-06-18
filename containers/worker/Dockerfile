FROM python:3.10-slim

WORKDIR /app

# Copy only the necessary files first to leverage Docker's build cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install-deps
RUN playwright install

# Copy application code
COPY database/ ./database/
COPY langchain_app/ ./langchain_app/
COPY workers/ ./workers/
COPY amazon_scraper/ ./amazon_scraper/

# Create any necessary directories
RUN mkdir -p /app/logs

# Set Python path
ENV PYTHONPATH=/app

# The command will be provided at runtime via the entry point script
CMD ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info", "--concurrency=1", "--queues=analysis_agent"]
