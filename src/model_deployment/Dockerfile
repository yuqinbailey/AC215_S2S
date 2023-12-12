# Use the base PyTorch image as it comes with PyTorch and CUDA pre-installed
FROM pytorch/pytorch:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    openjdk-11-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Set the working directory in the Docker container
WORKDIR /workspace

# Install the necessary Python packages from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install TorchServe and torch-model-archiver
RUN pip install --no-cache-dir torchserve torch-model-archiver

# Create the directories used in handler.py
RUN mkdir -p /workspace/model_store /workspace/processed_data/playing_bongo /workspace/features/playing_bongo /workspace/results

# Copy the src directory and handler.py to the container
COPY src /workspace/src
COPY handler.py /workspace/
COPY config.properties /workspace/

# Ensure Python will discover the modules in /workspace/src
ENV PYTHONPATH "${PYTHONPATH}:/workspace/src"

# Copy the model archive file to the container
COPY model_store/s2s.mar /workspace/model_store/

# Expose the ports that TorchServe uses
EXPOSE 8080 8081