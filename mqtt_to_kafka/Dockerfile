# Use a slim Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY mqtt_to_kafka.py .

# Run the application using the -u flag for unbuffered output
CMD ["python", "-u", "mqtt_to_kafka.py"]