FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install cryptography package
RUN pip install --no-cache-dir cryptography

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/
COPY setup.py .

# Install the package in development mode
RUN pip install -e .

# Expose port for web interface
EXPOSE 5000

# Set environment variables
ENV METABASE_URL=http://localhost:3000
ENV METABASE_API_KEY=""
ENV PYTHONUNBUFFERED=1

# Use entrypoint script to allow different commands
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"] 