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
RUN conda create -n myenv python=3.7.2 && \
    conda install -n myenv -c conda-forge ffmpeg && \
    conda clean -a -y

# Copy requirements and install
COPY requirements.txt /
RUN /opt/conda/envs/myenv/bin/pip install --no-cache-dir -r /requirements.txt

# Install additional dependencies
RUN wget http://es.archive.ubuntu.com/ubuntu/pool/main/libf/libffi/libffi7_3.3-4_amd64.deb && \
    dpkg -i libffi7_3.3-4_amd64.deb

RUN conda install -y pytorch==1.9 torchvision torchaudio cudatoolkit=11.1 -c pytorch -c nvidia

# Set working directory and copy app contents
COPY . /app
WORKDIR /app

# Initialize conda for bash and activate environment
RUN conda init bash && \
    echo "conda activate myenv" >> ~/.bashrc
