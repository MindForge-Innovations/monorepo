# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ./src /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
ENTRYPOINT ["python3", "bot-notifier.py"]
