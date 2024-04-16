#!/bin/bash

# Check if Docker daemon is running
if ! systemctl is-active --quiet docker; then
    echo "Docker daemon is not running. Starting Docker..."
    sudo systemctl start docker

    # Wait for Docker to start and become ready
    while ! systemctl is-active --quiet docker; do
        echo "Waiting for Docker to start..."
        sleep 1
    done
fi

echo "Docker daemon is running."

# Run docker-compose up
echo "Running docker-compose up..."
docker-compose up
