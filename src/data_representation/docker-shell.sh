#!/bin/bash

set -e

# Create the network if we don't have it yet
docker network inspect data-representation-network >/dev/null 2>&1 || docker network create data-representation-network

# # Build the image based on the Dockerfile
# docker build -t data-representation --platform=linux/arm64/v8 -f Dockerfile .

# Run All Containers
docker-compose run --rm --name data-representation -ti -v "$(pwd)":/app data-representation /bin/bash