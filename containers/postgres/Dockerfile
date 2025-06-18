FROM postgres:17

# Copy the initialization SQL script into the container
COPY database/00_init.sql /docker-entrypoint-initdb.d/

# Environment variables will be provided at runtime
