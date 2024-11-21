# Use a base image compatible with Raspberry Pi (e.g., a Python image)
FROM arm32v7/python:3.9-slim

# Set environment variables for non-interactive installation (to avoid prompts)
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Pygame and Kuksa client
RUN apt-get update && \
    apt-get install -y \
    libfreetype6-dev \
    libSDL2-dev \
    libsdl2-image-dev \
    libportmidi-dev \
    libsmpeg-dev \
    libsdl2-mixer-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libjpeg-dev \
    libopenal-dev \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install pygame kuksa-client grpcio

# Set the working directory inside the container
WORKDIR /app

# Copy your Python script into the container
COPY dashboard.py /app/dashboard.py

# Set the environment variables for the Kuksa client (optional)
ENV BROKER_ADDRESS="192.168.1.99"
ENV BROKER_PORT=55555

# Command to run the Python script when the container starts
CMD ["python", "vehicle_dashboard.py"]
