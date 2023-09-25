Silent to Sound: Video Sound Generator
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
            ├── data_collection
            │   ├── Dockerfile
            │   ├── docker-compose.yml
            │   ├── docker-shell.sh
            │   ├── Pipfile
            │   ├── Pipfile.lock
            │   └── collect.py
            ├── preprocessing
            │   ├── Dockerfile
            │   ├── docker-compose.yml
            │   ├── docker-shell.sh
            │   ├── Pipfile
            │   ├── Pipfile.lock
            │   └── preprocess.py
            └── validation
                ├── Dockerfile
                ├── docker-compose.yml
                ├── docker-shell.sh
                ├── Pipfile
                ├── Pipfile.lock
                └── data_split.txt


--------
# AC215 - Milestone2 - Silent to Sound

**Team Members**
Yuqin (Bailey) Bai, Danning (Danni) Lai, Tiantong Li, Yong Zhang, Yujan Ting, and Hanlin Zhu

**Group Name**
S2S (*Silent to Sound*)

**Project**

We aim to develop an application that generates ambient sounds from images or silent videos leveraging computer vision and multimodal models. Our goal is to enrich the general user experience by creating a harmonized visual-audio ecosystem, and facilitate immersive multimedia interactions for individuals with visual impairments.

### Milestone2 ###


**Data collection container**
- Input
- Ouput

(1) `src/data_collection/collect.py` - 

(2) `src/data_collection/Dockerfile` - 

(3) `src/data_collection/docker-compose.yml` - 

(4) `src/data_collection/docker-shell.sh` - 

(5) `src/data_collection/Pipfile` - 


**Preprocess container**
- Input to this container is source and destincation GCS location, parameters for resizing, secrets needed - via docker
- Output from this container stored at GCS location

(1) `src/preprocessing/preprocess.py` - the primary application logic for data preprocessing. We trim the video files into 10 seconds. It has the following function components. The script also provides three flags as command-line argument: `-d` for downloading videos from GCS, `-c` for cutting videos, and `-u` for uploading processed videos to GCS.
- `cut_video()`: trims 10-second segments from each video starting at the times specified in the 'vggsound.csv'. If the video doesn't have a full 10 seconds left from the start time, the subclip method will trim it to the end of the video.
- `makedirs()`: set up local directories for storing raw videos and cut videos.
- `download()`: downloads video files and related `vggsound.csv` from GCS to local directories.
- `upload()`: uploads processed video files from the local directory to GCS.

(2) `src/preprocessing/Dockerfile` - provides instructions for building the docker image for the data-preprocess service. The image is based on `python:3.9-slim-buster`. The working directory is set to `/app`.

(3) `src/preprocessing/docker-compose.yml` - specifies the data-preprocess service with the following configurations.
- Image name: data-preprocess
- Container name: data-preprocess
- GCP environment variables

(4) `src/preprocessing/docker-shell.sh` - set up and run the docker container.

(5) `src/preprocessing/Pipfile` - specifies the Python dependencies for the module.

Step-by-step instructions to run the docker container - 

```shell
git clone https://github.com/yuqinbailey/AC215_S2S.git
cd AC215_S2S/src/preprocessing
chmod +x docker-shell.sh
./docker-shell.sh
```


**Cross validation, data versioning container**
- This container reads preprocessed dataset and creates validation split and uses dvc for versioning
- Input to this container is source GCS location, parameters if any, secrets needed - via docker
- Output is flat file with train, validation, and test splits
  
(1) `src/validation/collect.py` - `-t` for the percentage of data to be used for training, and `-v` for the percentage of data to be used for validation, and the rest of data will be used for test.

(2) `src/validation/Dockerfile` - 

(3) `src/validation/docker-compose.yml` - 

(4) `src/validation/docker-shell.sh` - 

(5) `src/validation/Pipfile` - 

To run Dockerfile - `Instructions here`

**Notebooks** 
This folder contains code that is not part of container. 