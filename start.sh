#!/bin/bash

# Check if Docker daemon is running
if ! systemctl is-active --quiet docker; then
    echo "Docker daemon is not running. Starting Docker..."
    sudo systemctl start docker

    # Wait for Docker to start and become fully ready
    echo "Waiting for Docker to become ready..."
    until sudo docker info >/dev/null 2>&1; do
        sleep 1
        echo -n "."
    done
    echo "Docker is ready."
else
    echo "Docker daemon is already running."
fi

echo "Running docker-compose up..."
docker-compose up
