Silence to Sound: Generate Visually Aligned Sound for Videos
==============================

AC215 - Milestone5

Project Organization
------------
      .
      ├── LICENSE
      ├── README.md
      ├── notebooks
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

**GCP Bucket** 
`s2s_data_new`
```
  ├── vggsound.csv
  ├── raw_data                <- raw data scraped from youtube
  ├── processed_data          <- intermediate preprocessed data
  ├── features                <- extracted features from preprocessed data
  │   ├── filelists                 <- splited train and test sets
  │   └── playing_bingo
  │       ├── feature_flow_bninception_dim1024_21.5fps
  │       ├── feature_rgb_bninception_dim1024_21.5fps
  │       └── melspec_10s_22050hz          <- audio feature
  ├── dvc_store               <- data registry: yuqinbailey/s2s-dvcrepo
  ├── ckpt
  └── model                   <- saved model + update signitures
```


--------
# AC215 - Milestone5 - Silence to Sound

**Team Members**
Yuqin (Bailey) Bai, Danning (Danni) Lai, Tiantong Li, Yujan Ting, Yong Zhang, and Hanlin Zhu

**Group Name**
S2S (*Silence to Sound*)

**Project**

We aim to develop an application that generates ambient sounds from images or silent videos leveraging computer vision and multimodal models. Our goal is to enrich the general user experience by creating a harmonized visual-audio ecosystem, and facilitate immersive multimedia interactions for individuals with visual impairments.


### Code Structure

The following are the folders from the previous milestones:
```
- data_collection
- data_preprocessing
- feature_extraction
- train
- model_deployment
- workflow
```


## Milestone5
After completions of building a robust ML Pipeline in our previous milestone we have built a backend api service and frontend app. This will be our user-facing application that ties together the various components built in previous milestones.

**Application Design**

Before we start implementing the app we built a detailed design document outlining the application’s architecture. We built a Solution Architecture abd Technical Architecture to ensure all our components work together.

Here is our Solution Architecture:
<img src="images/solution_arch.png"  width="800">

Here is our Technical Architecture:
<img src="images/technical_arch.png"  width="800">


### App backend API container


### App frontend container
<img src="images/frontend_running.jpg"  width="800">


### Docker cleanup
To make sure we do not have any running containers and clear up unused images -
* Run `docker container ls`
* Stop any container that is running
* Run `docker image ls`
* Run `docker system prune`


### [References](references/README.md)
