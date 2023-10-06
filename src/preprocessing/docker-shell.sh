#!/bin/bash

set -e

# Create the network if we don't have it yet
docker network inspect data-preprocess-network >/dev/null 2>&1 || docker network create data-preprocess-network

# Build the image based on the Dockerfile
docker build -t data-preprocess --platform=linux/arm64/v8 -f Dockerfile .

# Run All Containers
docker-compose run --rm --service-ports data-preprocess