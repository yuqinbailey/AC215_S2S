#!/bin/bash

echo "Container is running!!!"

args="$@"
echo $args

if [[ -z ${args} ]]; 
then
    # if no args
    echo "executing if!!!"
    # Authenticate gcloud using service account
    gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
    # Set GCP Project Details
    gcloud config set project $GCP_PROJECT
    #/bin/bash
    pipenv shell
else
  echo "executing else!!!"
  pipenv run python $args
fi