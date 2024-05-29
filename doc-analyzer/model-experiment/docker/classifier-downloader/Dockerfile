FROM python:3.11-slim
RUN pip install omegaconf colorlog rootutils boto3 python-dotenv label-studio-sdk tqdm
COPY ./src/ /app/src/
COPY ./requirements.txt /app/
COPY ./.project-root /app/
WORKDIR /app
CMD ["python", "src/scripts/dataset_downloader.py"]
