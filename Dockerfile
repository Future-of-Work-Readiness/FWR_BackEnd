FROM python:3.11-slim

# Install PostgreSQL client for health checks
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app

# Copy data files for population (must be in Backend/data relative to app directory)
COPY ./data /app/data

# The auto_populate_if_empty() runs automatically in main.py on startup
# Population happens after tables are created and database connection is established
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
