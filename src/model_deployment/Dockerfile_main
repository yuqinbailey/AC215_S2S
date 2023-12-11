# # Use the official Debian-hosted Python image
# FROM python:3.9-slim-buster

# ARG DEBIAN_PACKAGES="build-essential git curl wget unzip gzip"

# # Prevent apt from showing prompts
# ENV DEBIAN_FRONTEND=noninteractive

# # Python wants UTF-8 locale
# ENV LANG=C.UTF-8

# # Tell pipenv where the shell is. This allows us to use "pipenv shell" as a
# # container entry point.
# ENV PYENV_SHELL=/bin/bash

# # Tell Python to disable buffering so we don't lose any logs.
# ENV PYTHONUNBUFFERED=1

# # Ensure we have an up to date baseline, install dependencies and
# # create a user so we don't run the app as root
# RUN set -ex; \
#     for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
#     apt-get update && \
#     apt-get upgrade -y && \
#     apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
#     apt-get install -y --no-install-recommends software-properties-common apt-transport-https ca-certificates gnupg2 gnupg-agent curl openssh-client && \
#     curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
#     echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
#     curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends google-cloud-sdk && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/* && \
#     pip install --no-cache-dir --upgrade pip && \
#     pip install pipenv && \
#     useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
#     mkdir -p /app && \
#     chown app:app /app

# Copy the service account key
# ENV GOOGLE_APPLICATION_CREDENTIALS=model-deployment.json
# ENV GCP_PROJECT="ac215project-398818"
# ENV GCS_MODELS_BUCKET_NAME="gs://s2s_data"

# # Switch to the new user
# USER app
# WORKDIR /app

# # Install python packages
# ADD --chown=app:app Pipfile Pipfile.lock /app/

# RUN pipenv sync

# # Add the rest of the source code. This is done last so we don't invalidate all
# # layers when we change a line of code.
# ADD --chown=app:app . /app

# # Entry point
# ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]

# Start with an official PyTorch base image
FROM pytorch/pytorch:1.2-cuda10.0-cudnn7-runtime

# Set environment variables for non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libxrender1 \
    fish \
    vim \
    screen \
    wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a new Conda environment and install packages
RUN conda create -n myenv python=3.9 && \
    conda install -n myenv -c conda-forge ffmpeg && \
    conda clean -a -y

# Copy requirements and install
COPY requirements.txt /
RUN /opt/conda/envs/myenv/bin/pip install --no-cache-dir -r /requirements.txt

# Install additional dependencies
RUN wget http://es.archive.ubuntu.com/ubuntu/pool/main/libf/libffi/libffi7_3.3-4_amd64.deb && \
    dpkg -i libffi7_3.3-4_amd64.deb

RUN conda install -n myenv -y pytorch==1.9 torchvision torchaudio cudatoolkit=11.1 -c pytorch -c nvidia && \
    conda clean -a -y

# Set working directory and copy app contents
COPY . /app
WORKDIR /app

# Initialize conda for bash and activate environment
RUN conda init bash && \
    echo "conda activate myenv" >> ~/.bashrc