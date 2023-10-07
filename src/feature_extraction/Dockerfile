# Start with an official PyTorch base image
FROM pytorch/pytorch:1.2-cuda10.0-cudnn7-runtime

# Set the maintainer label
LABEL maintainer="yujanting@hms.harvard.edu"

# Set environment variables to non-interactive (this prevents some prompts)
ENV DEBIAN_FRONTEND=noninteractive

# Create a new Conda environment and install packages
RUN conda create -n myenv python=3.7.2 && \
    conda install -n myenv -c conda-forge ffmpeg && \
    conda install -n myenv torchvision==0.4.0 cudatoolkit=10.0 -c pytorch && \
    conda clean -a -y

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    libglib2.0-0 libsm6 libxrender1 fish vim screen \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Additional apt packages installation
RUN apt update && apt install -y libsm6 libxext6 libxrender-dev

# Upgrade Pillow
RUN /opt/conda/envs/myenv/bin/pip install --upgrade Pillow

RUN sed -i 's/from PIL import Image, ImageOps, ImageEnhance, PILLOW_VERSION/from PIL import Image, ImageOps, ImageEnhance, __version__ as PILLOW_VERSION/' /opt/conda/envs/myenv/lib/python3.7/site-packages/torchvision/transforms/functional.py


# Activate the new environment and install additional dependencies
COPY requirements.txt /
RUN /opt/conda/envs/myenv/bin/pip install --no-cache-dir -r /requirements.txt

# cuda 10 pytorch
RUN /opt/conda/envs/myenv/bin/pip install torch==1.4.0 torchvision==0.5.0 -f https://download.pytorch.org/whl/cu100/torch_stable.html
RUN conda install -n myenv pytorch torchvision cudatoolkit=10.0 -c pytorch

# Upgrade Librosa and its dependencies
RUN /opt/conda/envs/myenv/bin/pip install --upgrade librosa numpy scipy scikit-learn joblib decorator resampy numba


RUN apt-get update && apt-get install -y wget && \
    wget http://es.archive.ubuntu.com/ubuntu/pool/main/libf/libffi/libffi7_3.3-4_amd64.deb && \
    dpkg -i libffi7_3.3-4_amd64.deb
    
COPY . /app
WORKDIR /app

RUN conda init bash
RUN echo "conda activate myenv" >> ~/.bashrc