FROM python:3.11-slim
COPY ./src/ /app/src/
COPY ./requirements.txt /app/
COPY ./.project-root /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "src/scripts/train_classification.py"]

