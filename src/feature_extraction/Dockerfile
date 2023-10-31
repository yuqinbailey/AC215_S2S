# Start with a base image
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

# Now proceed with conda installations and the rest of your Dockerfile
RUN conda create -n myenv python=3.7.2 && \
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

# Copy the entrypoint script into the image
COPY entrypoint.sh /entrypoint.sh

# Set permissions for the entrypoint script
RUN chmod +x /entrypoint.sh

# Set working directory and copy app contents
COPY . /app
WORKDIR /app

# Set the entrypoint script as the ENTRYPOINT
ENTRYPOINT ["/entrypoint.sh"]

# Set a default CMD
CMD ["/bin/bash"]

