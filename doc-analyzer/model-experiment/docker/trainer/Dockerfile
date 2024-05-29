FROM python:3.11-slim
# CPU version only, much lighter
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu 
RUN pip install lightning omegaconf colorlog rootutils boto3 python-dotenv tqdm seaborn mlflow
WORKDIR /app
COPY ./src/ /app/src/
COPY .project-root /app/.project-root
CMD ["python", "src/scripts/train_classification.py"]