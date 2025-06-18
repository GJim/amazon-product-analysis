#!/bin/bash

# Generate a random password
REDIS_PASSWORD=$(openssl rand -base64 12)

# Echo the generated password to the terminal
echo "Generated Redis password: $REDIS_PASSWORD"

# Create a docker network if it doesn't exist
docker network create amazon_product_analysis_network 2>/dev/null || true

# Create a custom Redis configuration file with the generated password
cat > containers/redis/redis.conf <<EOF
# Redis configuration
requirepass $REDIS_PASSWORD
EOF

# Run the Redis container
docker run -d \
  --name redis \
  --network amazon_product_analysis_network \
  -p 6379:6379 \
  -v $(pwd)/containers/redis/redis.conf:/usr/local/etc/redis/redis.conf \
  $(docker build -q -t redis_custom containers/redis) \
  redis-server /usr/local/etc/redis/redis.conf

echo "Redis container started with password: $REDIS_PASSWORD"
echo "Redis connection settings for other services:"
echo "  REDIS_HOST=redis"
echo "  REDIS_PORT=6379"
echo "  REDIS_PASSWORD=$REDIS_PASSWORD"
