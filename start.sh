#!/bin/bash

# Check if Docker daemon is running
if ! systemctl is-active --quiet docker; then
    echo "Docker daemon is not running. Starting Docker..."
    sudo systemctl start docker
fi

# Ensure Docker is fully operational
while ! docker info > /dev/null 2>&1; do
    echo "Waiting for Docker to be fully operational..."
    sleep 1
done

echo "Docker daemon is running and ready."

# Run docker-compose up
echo "Running docker-compose up..."
docker-compose up
