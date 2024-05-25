FROM pytorch/pytorch
RUN pip install omegaconf colorlog rootutils boto3 python-dotenv tqdm seaborn mlflow

COPY ./src/ /app/src/

CMD ["python", "src/scripts/train_classification.py"]