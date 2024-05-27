FROM pytorch/pytorch
RUN pip install lightning omegaconf colorlog rootutils boto3 python-dotenv tqdm seaborn mlflow
WORKDIR /app
# COPY requirements.txt /app/
# RUN pip install -r requirements.txt
COPY ./src/ /app/src/
COPY .project-root /app/.project-root
CMD ["python", "src/scripts/train_classification.py"]