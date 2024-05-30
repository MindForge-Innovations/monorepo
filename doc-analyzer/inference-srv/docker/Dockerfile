FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install Pillow mlflow
WORKDIR /app
COPY ./src/ /app/
COPY ./src/model.pt /app/model.pt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
