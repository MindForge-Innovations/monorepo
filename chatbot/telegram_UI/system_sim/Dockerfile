FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and appbis.py into the container
COPY requirements.txt systemSimulator.py ./

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt


# Expose the port 5000
EXPOSE 8000
# Command to run the Flask app
#CMD ["sh", "-c", "python3 "]
ENTRYPOINT ["python3", "systemSimulator.py"]

