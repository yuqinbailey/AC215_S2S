CUSTOM_PREDICTOR_IMAGE_URI="gcr.io/ac215project-398818/pytorch_predict_regnet"
docker build --tag=$CUSTOM_PREDICTOR_IMAGE_URI .
# docker run -t -d --rm -p 7080:7080 $CUSTOM_PREDICTOR_IMAGE_URI
# gcloud auth login
# gcloud auth configure-docker
# docker push $CUSTOM_PREDICTOR_IMAGE_URI
