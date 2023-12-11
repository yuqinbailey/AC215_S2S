#!/bin/bash

set -e

# Create the network if we don't have it yet
docker network inspect data-preprocessing-network >/dev/null 2>&1 || docker network create data-preprocessing-network

# Build the image based on the Dockerfile
docker build -t data-preprocessing --platform=linux/arm64 -f Dockerfile .

# Run All Containers
docker-compose run --rm --service-ports data-preprocessing