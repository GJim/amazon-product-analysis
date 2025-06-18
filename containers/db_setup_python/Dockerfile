FROM python:3.10-slim

WORKDIR /app

# Copy only the necessary files
COPY database/ /app/database/
COPY setup_database.py /app/
COPY requirements.txt /app/

# Install only the required packages for database setup
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary

# The script will be executed when the container is run
CMD ["python", "setup_database.py"]
