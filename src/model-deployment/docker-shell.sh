# #!/bin/bash

# set -e

# export IMAGE_NAME=model-deployment-cli
# export BASE_DIR=$(pwd)
# export SECRETS_DIR=$(pwd)/../secrets/
# export GCP_PROJECT="ac215project-398818"
# export GCS_MODELS_BUCKET_NAME="gs://s2s_data"


# # Build the image based on the Dockerfile
# #docker build -t $IMAGE_NAME -f Dockerfile .
# # M1/2 chip macs use this line
# docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# # Run Container
# docker run --rm --name $IMAGE_NAME -ti \
# -v "$BASE_DIR":/app \
# -v "$SECRETS_DIR":/secrets \
# -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/model-deployment.json \
# -e GCP_PROJECT=$GCP_PROJECT \
# -e GCS_MODELS_BUCKET_NAME=$GCS_MODELS_BUCKET_NAME \
# $IMAGE_NAME

#!/bin/bash

# This is a shell option that tells the script to exit immediately if any command returns a non-zero exit status.
set -e

# Create the network if we don't have it yet
docker network inspect model-deployment-network >/dev/null 2>&1 || docker network create model-deployment-network

# Build the image based on the Dockerfile
docker build -t model-deployment-cli --platform=linux/arm64/v8 -f Dockerfile .

# Run All Containers
docker-compose run --rm --name model-deployment -ti -v "$(pwd)":/app model-deployment /bin/bash