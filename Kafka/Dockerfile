# Use a Python base image
FROM python:3.9-slim

EXPOSE 5000
# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Set the default command to run your Python script (this will be overridden by docker-compose.yml)
CMD ["python", "producer.py"]
