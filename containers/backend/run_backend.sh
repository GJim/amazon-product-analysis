#!/bin/bash

# Check if postgres password is provided
if [ -z "$1" ]; then
  echo "Error: Postgres password not provided"
  echo "Usage: ./run_backend.sh <postgres_password> <redis_password>"
  exit 1
fi

# Check if redis password is provided
if [ -z "$2" ]; then
  echo "Error: Redis password not provided"
  echo "Usage: ./run_backend.sh <postgres_password> <redis_password>"
  exit 1
fi

POSTGRES_PASSWORD=$1
REDIS_PASSWORD=$2

# Create a docker network if it doesn't exist
docker network create amazon_product_analysis_network 2>/dev/null || true

# Build the backend container
docker build -t backend -f containers/backend/Dockerfile .

# Run the backend container
docker run -d \
  --name backend \
  --network amazon_product_analysis_network \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  -e PORT=8000 \
  -e DB_USERNAME=postgres \
  -e DB_PASSWORD=$POSTGRES_PASSWORD \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=amazon_product_analysis \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD=$REDIS_PASSWORD \
  -e REDIS_DB=0 \
  -e REDIS_CHANNEL_PREFIX=product_analysis \
  -e ALLOWED_ORIGINS=http://localhost:80 \
  backend

echo "Backend container is running on http://localhost:8000"
echo "It is configured to connect to:"
echo "  - Postgres on host 'postgres' with the provided password"
echo "  - Redis on host 'redis' with the provided password"
