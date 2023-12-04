#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e
set -x

# Define some environment variables
#export IMAGE_NAME="lildanni/s2s-api-service"
export IMAGE_NAME="s2s-api-service:arm"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
export PERSISTENT_DIR=$(pwd)/../../persistent-folder/
export GCS_BUCKET_NAME="s2s_data_new"

# Build the image based on the Dockerfile
# docker build -t $IMAGE_NAME -f Dockerfile .

# M1/2 chip macs use this line
# local use arm
docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .
#docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

docker run --rm --name api-service -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$PERSISTENT_DIR":/persistent \
-p 9000:9000 \
-e DEV=1 \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/ml-workflow.json \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
$IMAGE_NAME