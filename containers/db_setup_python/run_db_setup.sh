#!/bin/bash

# Check if we have the Postgres password
if [ -z "$1" ]; then
  echo "Error: Postgres password not provided"
  echo "Usage: ./run_db_setup.sh <postgres_password>"
  exit 1
fi

POSTGRES_PASSWORD=$1

# Build the Python database setup container
docker build -t db_setup_python containers/db_setup_python

# Run the container with environment variables and remove it when done
docker run --rm \
  --network amazon_product_analysis_network \
  -e DB_USERNAME=postgres \
  -e DB_PASSWORD=$POSTGRES_PASSWORD \
  -e DB_HOST=postgres \
  -e DB_PORT=5432 \
  -e DB_NAME=amazon_product_analysis \
  db_setup_python

echo "Database tables have been initialized"
echo "The temporary Python container has been removed"
