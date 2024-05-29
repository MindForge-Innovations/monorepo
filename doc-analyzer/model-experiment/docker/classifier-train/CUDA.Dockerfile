# Use the CUDA 11.5 base image with cuDNN 8
FROM nvidia/cuda:11.5.2-cudnn8-runtime-ubuntu20.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CUDA 11.5 support
RUN pip install torch==1.10.0+cu115 torchvision==0.11.1+cu115 torchaudio==0.10.0+cu115 -f https://download.pytorch.org/whl/cu115/torch_stable.html

# Install additional Python packages
RUN pip install lightning omegaconf colorlog rootutils boto3 python-dotenv tqdm seaborn mlflow

# Set the working directory
WORKDIR /app

# Copy application code
COPY ./src/ /app/src/
COPY .project-root /app/.project-root

# Command to run your application
CMD ["python", "src/scripts/train_classification.py"]
