#!/bin/bash

set -e

# Create the network if we don't have it yet
docker network inspect feature-extraction-network >/dev/null 2>&1 || docker network create feature-extraction-network

# Build the image based on the Dockerfile
# docker build -t feature-extraction --platform=linux/arm64/v8 -f Dockerfile .

# Run All Containers
docker-compose run --rm --name feature-extraction -ti -v "$(pwd)":/app feature-extraction /bin/bash