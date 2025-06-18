#!/bin/bash

# Generate a random password
POSTGRES_PASSWORD=$(openssl rand -base64 12)

# Echo the generated password to the terminal
echo "Generated Postgres password: $POSTGRES_PASSWORD"

# Create a docker network if it doesn't exist
docker network create amazon_product_analysis_network 2>/dev/null || true

# Run the Postgres container
docker run -d \
  --name postgres \
  --network amazon_product_analysis_network \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  -v $(pwd)/database:/database \
  $(docker build -q -t postgres_custom containers/postgres)

echo "Postgres container started with password: $POSTGRES_PASSWORD"
echo "The database 'amazon_product_analysis' will be created using the initialization script"
echo "Database connection settings for other services:"
echo "  DB_HOST=postgres"
echo "  DB_PORT=5432"
echo "  DB_USERNAME=postgres"
echo "  DB_PASSWORD=$POSTGRES_PASSWORD"
echo "  DB_NAME=amazon_product_analysis"
