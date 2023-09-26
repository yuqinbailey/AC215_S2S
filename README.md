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
            ├── secrets
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
                └── data_split.py


**GCP Bucket** 
`s2s_data`
```
  ├── vggsound.csv
  ├── raw_data
  ├── processed_data
  └── dvc_store
```


--------
# AC215 - Milestone2 - Silent to Sound

**Team Members**
Yuqin (Bailey) Bai, Danning (Danni) Lai, Tiantong Li, Yong Zhang, Yujan Ting, and Hanlin Zhu

**Group Name**
S2S (*Silent to Sound*)

**Project**

We aim to develop an application that generates ambient sounds from images or silent videos leveraging computer vision and multimodal models. Our goal is to enrich the general user experience by creating a harmonized visual-audio ecosystem, and facilitate immersive multimedia interactions for individuals with visual impairments.


## Milestone2

```shell
git clone https://github.com/yuqinbailey/AC215_S2S.git
```


### Local secrets folder

Create a local secrets folder under `src` directory because we do not include any secure information in Git. Add the GCP service account private key, `data-service-account.json`, to this folder.


### Data collection container
- Input to this container is source and destination GCS location, parameters for resizing, and secrets needed - via docker. The program would pull the Youtube IDs from bucket
- Output: The pushed videos in the bucket

(1) `src/data_collection/collect.py` -
- `download_from_youtube()`: download the videos that are specified in the dataset from YouTube and push the video to the bucket. We skip over the already invalid videos.

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
- Output is flat file with train, validation, and test splits

  
(1) `src/validation/collect.py` - `-t` for the percentage of data to be used for training, and `-v` for the percentage of data to be used for validation, and the rest of data will be used for test.

(2) `src/validation/Dockerfile` - 

(3) `src/validation/docker-compose.yml` - 
- Image name: data-validation-version-cli
- Container name: data-validation-version-cli
- GCP environment variables

(4) `src/validation/docker-shell.sh` - 

(5) `src/validation/Pipfile` - 

To run Dockerfile -
```shell
cd ../validation
git init
chmod +x docker-shell.sh
./docker-shell.sh
```
Explanation: `dvc init` looks for the root of the Git repository and initializes there. In our case, we want DVC to work within a subdirectory, so we `git init` to initialize an empty git repository in this subdirectory.  

Inside the validation container, to split data - 
```shell
/app$ python data_split.py
```

Perform data-versioning -
```shell
/app$ dvc init
/app$ dvc remote add -d s2s_dataset gs://s2s_data/dvc_store
/app$ dvc add s2s_dataset
/app$ dvc push
```
Notice that we run `dvc init` only for the first time to initialize DVC in the subdirectory.

Commit DVC changes in the subdirectory
```shell
/app$ exit
git add .
git commit -m 'dataset changes'
```

Navigate one level up `cd ..`
Add changes  `git add validation/`
Commit changes `git commit -m 'Updates in the DVC subdirectory`
Add a dataset tag `git tag -a 'dataset_v1' -m 'tag dataset`
Push changes to main git repo`git push --atomic origin milestone2 dataset_v1`

### Docker cleanup
To make sure we do not have any running containers and clear up unused images -
* Run `docker container ls`
* Stop any container that is running
* Run `docker image ls`
* Run `docker system prune`


### Data visualization for sanity check
- [Colab Notebook](https://colab.research.google.com/drive/16ipwKR76L_exSH5SqfNyQ7FJUOtNSwla?usp=sharing)


### Notebooks

This folder contains code that is not part of container. 
