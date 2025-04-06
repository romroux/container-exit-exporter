#!/bin/bash
set -e

DOCKER_SOCKET="/var/run/docker.sock"

# Function to configure access to the Docker socket
setup_docker_access() {
    if [ -S "$DOCKER_SOCKET" ]; then
        DOCKER_GID=$(stat -c '%g' "$DOCKER_SOCKET")
#        echo "Docker socket GID: $DOCKER_GID"

        # Try to create a group with the same GID
        if getent group $DOCKER_GID > /dev/null 2>&1; then
             echo "Group already exists"
#            echo "Group with GID $DOCKER_GID already exists"
        else
             echo "Creating dockerhost group"
#            echo "Creating dockerhost group with GID $DOCKER_GID"
            addgroup -g "$DOCKER_GID" dockerhost
        fi

        # Create user if necessary
        if ! id exporter > /dev/null 2>&1; then
            echo "Creating exporter user"
            adduser -D -u 1000 exporter
        fi

        # Add user to the docker group
#        echo "Adding exporter user to group with GID $DOCKER_GID"
        adduser exporter $(getent group $DOCKER_GID | cut -d: -f1)

        # Adjust permissions
        chown -R exporter:$(getent group $DOCKER_GID | cut -d: -f1) /app

        # Display configurations
        echo "Starting exporter on port $EXPORTER_PORT"
        echo "Collection interval: $COLLECTION_INTERVAL seconds"

        # Run as non-root user
        exec su-exec exporter python /app/docker_exit_exporter.py
    else
        echo "ERROR: Docker socket not found at $DOCKER_SOCKET"
        exit 1
    fi
}

# Configuration and launch
setup_docker_access