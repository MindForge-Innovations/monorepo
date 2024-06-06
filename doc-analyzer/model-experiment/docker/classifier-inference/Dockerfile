FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install Pillow mlflow
WORKDIR /app
COPY ./src/scripts/inference.py /app/

EXPOSE 80

CMD ["uvicorn", "inference:app", "--host", "0.0.0.0", "--port", "80"]
