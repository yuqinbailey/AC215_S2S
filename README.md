Silent to Sound: Video Sound Generator
==============================

AC215 - Milestone3

Project Organization
------------
      ├── LICENSE
      ├── README.md
      ├── notebooks
      ├── references
      ├── requirements.txt
      ├── setup.py
      └── src
            ├── secrets
            ├── data_collection
            │   ├── ...
            │   └── collect.py
            ├── preprocessing
            │   ├── ...
            │   └── preprocess.py
            ├── validation          <- versioning
            │   └── ...
            ├── feature_extraction
            │   ├── Dockerfile
            │   ├── docker-shell.sh
            │   ├── Pipfile
            │   ├── Pipfile.lock
            │   └── 
            └── train
                ├── Dockerfile
                ├── docker-entrypoint.sh
                ├── docker-shell.sh
                ├── Pipfile
                ├── Pipfile.lock
                └── cli.sh


**GCP Bucket** 
`s2s_data`
```
  ├── vggsound.csv
  ├── raw_data
  ├── processed_data
  ├── features
  └── dvc_store
```


--------
# AC215 - Milestone3 - Silent to Sound

**Team Members**
Yuqin (Bailey) Bai, Danning (Danni) Lai, Tiantong Li, Yujan Ting, Yong Zhang, and Hanlin Zhu

**Group Name**
S2S (*Silent to Sound*)

**Project**

We aim to develop an application that generates ambient sounds from images or silent videos leveraging computer vision and multimodal models. Our goal is to enrich the general user experience by creating a harmonized visual-audio ecosystem, and facilitate immersive multimedia interactions for individuals with visual impairments.


## Milestone3

**Experiment Tracking**

**Serverless Training**


### Data collection container
- Input to this container is source and destination GCS location, parameters for resizing, and secrets needed - via docker. The program would pull the Youtube IDs from bucket
- Output: The pushed videos in the bucket

(1) `src/data_collection/collect.py` - `--nums_to_download` specifies the number of videos to download each time.
- `download_from_youtube()`: downloads the videos that are specified in the dataset from YouTube and push the video to the bucket. We skip over the already invalid videos.

(2) `src/data_collection/Dockerfile` - provides instructions for building the docker image for the data-preprocess service. The image is based on `python:3.9-slim-buster`. The working directory is set to `/app`.

(3) `src/data_collection/docker-compose.yml` - specifies the data-preprocess service with the following configurations.
- Image name: data-collection
- Container name: data-collection
- GCP environment variables

(4) `src/data_collection/docker-shell.sh` -  set up and run the docker container.

(5) `src/data_collection/Pipfile` - specifies the Python dependencies for the module.

Step-by-step instructions to run the docker container - 

```shell
cd AC215_S2S/src/data_collection
chmod +x docker-shell.sh
sh docker-shell.sh
```

Inside the collection container, we can run the following example command to collect 10 more videos - 
```shell
/app$ python collect.py --nums_to_download 10
/app$ exit
```

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

To run Dockerfile - 
```shell
cd ../preprocessing
chmod +x docker-shell.sh
./docker-shell.sh
```

Inside the preprocessing container, to preprocess data and exit - 
```shell
/app$ python preprocess.py -d -c -u
/app$ exit
```


### Cross validation, data versioning container
- This container reads preprocessed dataset and creates validation split and uses dvc for versioning
- Input to this container is source GCS location, parameters if any, secrets needed - via docker
- Output is flat file with train, validation, and test splits to DVC

  
(1) `src/validation/data_split.py` - `-t` for the percentage of data to be used for training, and `-v` for the percentage of data to be used for validation, and the rest of data will be used for test.
- `download()`: downloads the preprocessed video clips from GCS.
- `train_val_test_split()`: splits the videos into train, validation, and test sets based on provided ratio and stores them under correcsponding folders under `s2s_data/`.

(2) `src/validation/Dockerfile` - provides instructions for building the docker image for the data-preprocess service. The image is based on `python:3.8-slim-buster`. The working directory is set to `/app`.

(3) `src/validation/docker-compose.yml` - specifies the data-preprocess service with the following configurations. 
- Image name: data-validation-version-cli
- Container name: data-validation-version-cli
- GCP environment variables

(4) `src/validation/docker-shell.sh` - set up and run the docker container. 

(5) `src/validation/Pipfile` - specifies the Python dependencies for the module.

For data versioning, `dvc init` looks for the root of the Git repository and initializes there. In this case, we want DVC to work within the subdirectory, so we also need to initialize an empty git repository inside this subdirectory - 
```shell
cd ../validation
git init
```

To run Dockerfile -
```shell
chmod +x docker-shell.sh
./docker-shell.sh
```

Inside the validation container, to split data - 
```shell
/app$ python data_split.py -t .7 -v .2
```

We've already init dvc and set remote to `gs://s2s_data/dvc_store`. To perform data-versioning -
```shell
/app$ dvc add s2s_dataset
/app$ dvc push
/app$ exit
```

To add, tag, and commit DVC changes tracked in the main git repo - 
```shell
cd ..
git add validation/s2s_dataset.dvc
git commit -m 'dataset changes'
git tag -a 'dataset_v1' -m 'tag dataset'
git push --atomic origin main dataset_v1
```


### Docker cleanup
To make sure we do not have any running containers and clear up unused images -
* Run `docker container ls`
* Stop any container that is running
* Run `docker image ls`
* Run `docker system prune`


### Data visualization for sanity check
- [Colab Notebook](https://colab.research.google.com/drive/16ipwKR76L_exSH5SqfNyQ7FJUOtNSwla?usp=sharing) - facilitates the retrieval of various versions of our dataset managed by DVC, requiring GCP and GitHub authentication. It offers two functions, `dataset_metrics` and `show_examples`, to efficiently visualize dataset samples and display metrics, serving as sanity check for our data.


### Notebooks

This folder contains code that is not part of container. 


### [References](references/README.md)
