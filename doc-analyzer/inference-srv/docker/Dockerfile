FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install colorlog
COPY ./src/ /app/
COPY ./src/model.pt /app/model.pt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
