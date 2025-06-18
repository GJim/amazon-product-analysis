FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies and Gunicorn
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy the application code
COPY backend/ ./backend/
COPY database/ ./database/
COPY langchain_app/ ./langchain_app/
COPY workers/ ./workers/
COPY amazon_scraper/ ./amazon_scraper/

# Create necessary directories if they don't exist
RUN mkdir -p /app/logs

# Set Python path
ENV PYTHONPATH=/app

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Command to run Gunicorn with the FastAPI app
CMD ["gunicorn", "backend.app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--log-level", "info"]
