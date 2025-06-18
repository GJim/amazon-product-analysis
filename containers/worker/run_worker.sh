#!/bin/bash

# Check if postgres password is provided
if [ -z "$1" ]; then
  echo "Error: Postgres password not provided"
  echo "Usage: ./run_worker.sh <postgres_password> <redis_password>"
  exit 1
fi

# Check if redis password is provided
if [ -z "$2" ]; then
  echo "Error: Redis password not provided"
  echo "Usage: ./run_worker.sh <postgres_password> <redis_password>"
  exit 1
fi

POSTGRES_PASSWORD=$1
REDIS_PASSWORD=$2

# Prompt for OpenAI API key
read -p "Enter your OpenAI API key: " OPENAI_API_KEY

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Error: OpenAI API key is required"
  exit 1
fi

# Create a docker network if it doesn't exist
docker network create amazon_product_analysis_network 2>/dev/null || true

# Build the worker container
docker build -t worker -f containers/worker/Dockerfile .

# Run the worker container
docker run -d \
  --name worker \
  --network amazon_product_analysis_network \
  -e DB_USERNAME=postgres \
  -e DB_PASSWORD=$POSTGRES_PASSWORD \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=amazon_product_analysis \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD=$REDIS_PASSWORD \
  -e REDIS_DB=0 \
  -e REDIS_BROKER_DB=1 \
  -e REDIS_BACKEND_DB=2 \
  -e REDIS_CHANNEL_PREFIX=product_analysis \
  -e DEFAULT_LLM_MODEL=gpt-4o \
  -e DEFAULT_LLM_TEMPERATURE=0 \
  -e LOG_LEVEL=INFO \
  -e MAX_PRODUCTS_TO_ANALYZE=5 \
  -e MAX_REVIEWS_PER_PRODUCT=20 \
  -e MAX_PRODUCT_LIMIT_DB=10 \
  -e MAX_COMPETITIVE_LIMIT_DB=5 \
  -e MAX_SCRAPE_ATTEMPTS=20 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  worker

echo "Worker container is running"
echo "It is configured to connect to:"
echo "  - Postgres on host 'postgres' with the provided password"
echo "  - Redis on host 'redis' with the provided password"
echo "  - OpenAI API with the provided key"
