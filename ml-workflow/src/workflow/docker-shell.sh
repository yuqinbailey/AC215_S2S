

export IMAGE_NAME="s2s-workflow"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../../secrets/
export GCP_PROJECT="ac215project-398818" 
export GCS_BUCKET_NAME="s2s-ml-workflow" 
export GCS_SERVICE_ACCOUNT="ml-workflow@ac215project-398818.iam.gserviceaccount.com"
export GCP_REGION="us-east1"
export GCS_PACKAGE_URI="gs://s2s_data"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .
#docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .


# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v /var/run/docker.sock:/var/run/do#cker.sock \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$BASE_DIR/../data_collection":/data-collection \
-v "$BASE_DIR/../data_preprocessing":/data-preprocessing \
-v "$BASE_DIR/../feature-extraction":/feature-extraction \
-v "$BASE_DIR/../model-deployment":/model-deployment \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/ml-workflow.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e GCS_SERVICE_ACCOUNT=$GCS_SERVICE_ACCOUNT \
-e GCP_REGION=$GCP_REGION \
$IMAGE_NAME