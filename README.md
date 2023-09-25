AC215-Template (Milestone2)
==============================

AC215 - Milestone2

Project Organization
------------
      ├── LICENSE
      ├── README.md
      ├── notebooks
      ├── references
      ├── requirements.txt
      ├── setup.py
      └── src
            ├── preprocessing
            │   ├── Dockerfile
            │   ├── preprocess.py
            │   └── requirements.txt
            └── validation
                  ├── Dockerfile
                  ├── cv_val.py
                  └── requirements.txt


--------
# AC215 - Milestone2 - Silent to Sound

**Team Members**
Yuqin (Bailey) Bai, Danning (Danni) Lai, Tiantong Li, Yong Zhang, Yujan Ting, and Hanlin Zhu

**Group Name**
S2S (*Silent to Sound*)

**Project**

We aim to develop an application that generates ambient sounds from images or silent videos leveraging computer vision and multimodal models. Our goal is to enrich the general user experience by creating a harmonized visual-audio ecosystem, and facilitate immersive multimedia interactions for individuals with visual impairments.

### Milestone2 ###


**Preprocess container**
- Input to this container is source and destincation GCS location, parameters for resizing, secrets needed - via docker
- Output from this container stored at GCS location

(1) `src/preprocessing/preprocess.py`  - the primary application logic for data preprocessing. We trim the video files into 10 seconds. It has the following function components. The script also provides three flags as command-line argument: '-d' for downloading videos from GCS, '-c' for cutting videos, and '-u' for uploading processed videos to GCS.
- `cut_video()`: trims 10-second segments from each video starting at the times specified in the 'vggsound.csv'. If the video doesn't have a full 10 seconds left from the start time, the subclip method will trim it to the end of the video.
- `makedirs()`: set up local directories for storing raw videos and cut videos.
- `download()`: downloads video files and related 'vggsound.csv' from GCS to local directories.
- `upload()`: uploads processed video files from the local directory to GCS.

(2) `src/preprocessing/Dockerfile` - provides instructions for building the docker image for the data-preprocess service. The image is based on python:3.9-slim-buster. The working directory is set to /app.

(3) `src/preprocessing/docker-compose.yml` - specifies the data-preprocess service with the following configurations.
- Image name: data-preprocess
- Container name: data-preprocess
- GCP environment variables

(4) `src/preprocessing/docker-shell.sh` - set up and run the docker container.

(5) `src/preprocessing/Pipfile` - specifies the Python dependencies for the module.

Step-by-step instructions to run the docker container - 

            git clone https://github.com/yuqinbailey/AC215_S2S.git
            cd AC215_S2S/src/preprocessing
            chmod +x docker-shell.sh
            ./docker-shell.sh
            


**Cross validation, Data Versioning**
- This container reads preprocessed dataset and creates validation split and uses dvc for versioning.
- Input to this container is source GCS location, parameters if any, secrets needed - via docker
- Output is flat file with cross validation splits
  
(1) `src/validation/cv_val.py` - 

(2) `requirements.txt` - 

(3) `src/validation/Dockerfile` - 

To run Dockerfile - `Instructions here`

**Notebooks** 
This folder contains code that is not part of container. 