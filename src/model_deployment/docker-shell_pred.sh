CUSTOM_PREDICTOR_IMAGE_URI="leocheung1001/regnet_deploy"
docker build -f Dockerfile_pred --tag=$CUSTOM_PREDICTOR_IMAGE_URI .

# Leo
# docker run -ti --rm -p 7080:7080 gcr.io/ac215project-398818/pytorch_predict_regnet
# docker run -ti --rm -p 7080:7080 gcr.io/ac215project-398818/pytorch_predict_regnet  /bin/bash
# docker run -ti --rm -p 7080:7080 leo/deploy_regnet /bin/bash

# docker run -ti --rm -p 7080:7080 --mount type=bind,source=$(pwd),target=/home/model-server/ leo/deploy_regnet

# Frank
# docker run -it gcr.io/ac215project-398818/pytorch_predict_regnet /bin/bash

# gcloud auth login
# gcloud auth configure-docker
# docker push $CUSTOM_PREDICTOR_IMAGE_URI
