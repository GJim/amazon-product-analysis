#!/bin/bash

# Generate random passwords
POSTGRES_PASSWORD=$(tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 16)
REDIS_PASSWORD=$(tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 16)

# Echo the generated passwords to the terminal
echo "Generated Postgres password: $POSTGRES_PASSWORD"
echo "Generated Redis password: $REDIS_PASSWORD"

# Prompt for OpenAI API key
read -p "Enter your OpenAI API key: " OPENAI_API_KEY

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Error: OpenAI API key is required for the worker service"
  exit 1
fi

# Export the passwords as environment variables for docker-compose
export POSTGRES_PASSWORD
export REDIS_PASSWORD
export OPENAI_API_KEY

# Run docker-compose with the environment variables
docker compose up -d

echo "All services are running:"
echo "- Postgres: localhost:5432 (password: $POSTGRES_PASSWORD)"
echo "- Redis: localhost:6379 (password: $REDIS_PASSWORD)"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:80"
echo "- Worker is running with the provided OpenAI API key"
