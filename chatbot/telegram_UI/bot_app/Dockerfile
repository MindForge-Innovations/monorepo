# Use the redis alpine v6 image as the base image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and appbis.py into the container
COPY requirements.txt appBis.py ./

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port 5000
# EXPOSE 5000
# Command to run the Flask app
ENTRYPOINT ["python3", "appBis.py"]

