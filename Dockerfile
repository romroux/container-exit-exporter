FROM python:alpine

# Build arguments with default values
ARG EXPORTER_PORT=9090
ARG COLLECTION_INTERVAL=15

# Transfer arguments to environment variables
ENV EXPORTER_PORT=${EXPORTER_PORT} \
    COLLECTION_INTERVAL=${COLLECTION_INTERVAL} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Metadata
LABEL maintainer="DevOps Team"
LABEL description="Docker container exit code exporter for Prometheus"
LABEL version="1.0.0"

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install necessary utilities
RUN apk add --no-cache tini bash su-exec shadow

# Copy application files
COPY docker_exit_exporter.py /app/
COPY docker-entrypoint.sh /app/

# Set execution permissions
RUN chmod +x /app/docker-entrypoint.sh

# Expose port for Prometheus (using the argument value)
EXPOSE ${EXPORTER_PORT}

# Use tini as entrypoint for signal handling
ENTRYPOINT ["/sbin/tini", "--", "/app/docker-entrypoint.sh"]
