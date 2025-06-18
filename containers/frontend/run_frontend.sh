#!/bin/bash

# Create a docker network if it doesn't exist
docker network create amazon_product_analysis_network 2>/dev/null || true

# Build and run the frontend container
docker build -t frontend -f containers/frontend/Dockerfile .
docker run -d \
  --name frontend \
  --network amazon_product_analysis_network \
  -p 80:80 \
  frontend

echo "Frontend container is running on http://localhost:80"
