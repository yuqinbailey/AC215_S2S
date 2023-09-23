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

(1) `src/preprocessing/preprocess.py`  - 

(2) `src/preprocessing/requirements.txt` -  

(3) `src/preprocessing/Dockerfile` - 

To run Dockerfile - `Instructions here`

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