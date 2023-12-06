Silence to Sound: Generate Visually Aligned Sound for Videos
==============================

### Presentation  Video
* \<Link Here>

### Blog Post Link
*  \<Link Here>
---

Project Organization
------------
      .
      ├── LICENSE
      ├── README.md
      ├── references
      ├── setup.py
      └── src
            ├── secrets
            ├── workflow
            │   └── ...
            ├── data_collection            <- Scripts for dataset creation
            │   └── ...
            ├── data_preprocessing         <- Code for data processing
            │   └── ...
            ├── feature_extraction         <- Code for video feature extracion
            │   └── ...
            ├── train                      <- Model training, evaluation, and prediction code
            │   └── ...
            ├── api_service                <- Code for model deployment & App backend APIs
            │   ├── api
            │   │   ├── tsn
            │   │   ├── wavenet_vododer
            │   │   ├── extract_rgb_flow.py
            │   │   ├── extract_mel_spectrogram.py
            │   │   ├── extract_feature.py
            │   │   ├── model.py
            │   │   ├── api_model.py
            │   │   └── service.py
            │   ├── Dockerfile
            │   ├── docker-entrypoint.sh
            │   ├── docker-shell.sh
            │   ├── Pipfile
            │   └── Pipfile.lock
            └── frontend_simple            <- Code for App frontend
                ├── js
                ├── index.html
                ├── Dockerfile
                └── docker-shell.sh


--------
# AC215 - Final Project

**Team Members**
[Yuqin (Bailey) Bai](https://github.com/yuqinbailey), [Danning (Danni) Lai](https://github.com/dl3918), [Tiantong Li](https://github.com/frankli0731), [Yujan Ting](https://github.com/YujanTing), [Yong Zhang](https://github.com/leocheung1001), and [Hanlin Zhu](https://github.com/hzhu98)

**Group Name**
S2S (*Silence to Sound*)

**Project - Problem Definition**

We aim to develop an application that generates ambient sounds from images or silent videos leveraging computer vision and multimodal models. Our goal is to enrich the general user experience by creating a harmonized visual-audio ecosystem, and facilitate immersive multimedia interactions for individuals with visual impairments.


## Data Description 

## Proposed Solution

After completions of building a robust ML Pipeline in our previous milestone we have built a backend api service and frontend app. This will be our user-facing application that ties together the various components built in previous milestones.

**S2S App**

We built a user friendly frontend simple app to generate the sounds from slient videos using convolution-based models from the backend. Using the app a user can upload a short slient video and upload it. The app will generate the sounds for the video and the user can download the generated video. 

<img src="images/frontend1.png"  width="800">

**Kubernetes Deployment**

We deployed our frontend and backend to a kubernetes cluster to take care of load balancing and failover. We used ansible scripts to manage creating and updating the k8s cluster. Ansible helps us manage infrastructure as code and this is very useful to keep track of our app infrastructure as code in GitHub. It helps use setup deployments in a very automated way.

### Code Structure

The following are the folders from the previous milestones:
```
- data_collection
- data_preprocessing
- feature_extraction
- train
- workflow
- api_service
- frontend_simple
- deployment
```


### App backend API container

This container has all the python files to run and expose the backend apis.

We built backend api service using FAST API to expose model functionality to the frontend. We provide the following functions for listening to the front-end. Some user-friendly prompts are also returned to the user while the model is doing the inference, such as progress bar.

<img src="images/backend1.jpg"  width="800">


### App frontend container

This container contains all the files to develop and build a web app. There are dockerfiles for both development and production.


### Deployment

This container helps manage building and deploying all our app containers. The deployment is to GCP and all docker images go to GCR. 

Here is our deployed app on a single VM instance with T4 GPU in GCP:
<img src="images/vm.png"  width="800">

To run the container locally:
- run api-service container
```shell
sh shell.sh
```

- run frontend container
```shell
sudo docker pull lildanni/s2s-frontend
sudo docker run -d --name frontend -p 3000:80 --network s2s lildanni/s2s-frontend
```

- run NGINX web server
```shell
sudo docker run -d --name nginx -v $(pwd)/conf/nginx/nginx.conf:/etc/nginx/nginx.conf -p 80:80 --network s2s nginx:stable
```

### Deploy using GitHub Actions


### [References](references/README.md)
