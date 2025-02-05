# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts during the install
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install Python, pip, v4l-utils, and other dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*
	
	# apt update
	# apt install wine64

# Install Python dependencies (optional)
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the work folder from your host machine to the container
COPY . /app/

# Install dependencies using Windows Python
# RUN /mnt/c/Windows/System32/cmd.exe /C "C:/tools/Python/python.exe -m pip install -r C:/tools/docker_containers/notraffic_ubuntu_container/requirements.txt"

# Install OpenCV or other Python dependencies (optional)
# RUN pip3 install opencv-python

# Set the working directory inside the container
WORKDIR /app

# Start Python Command
CMD ["/mnt/c/Windows/System32/cmd.exe", "/C", "C:/tools/Python/python.exe", "C:/tools/docker_containers/notraffic_ubuntu_container/DirectShow_to_capture_frames_in_Python.py"]


# Navigate to the container folder
# cd /mnt/c/tools/docker_containers/notraffic_ubuntu_container

# Build the docker image:
# sudo docker build -t ubuntu-camera-control .

# Run the Docker Image:
# docker run --rm -it --device=/dev/video0 ubuntu-camera-control bash
