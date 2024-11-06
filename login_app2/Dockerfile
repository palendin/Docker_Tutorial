# Use a lightweight Python image as the base
FROM python:3.8.0-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the message_board_app folder (including board and __init__.py)
COPY . .

# Install dependencies (assuming requirements.txt is in the root directory)
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Command to run when the container starts (specifying the script). The path refers to the path within the container's file after copying the scripts
CMD ["python", "/app/app.py"]


# The files you copy to the Docker image are stored in a virtual file system within the container. 
# This file system is created when the container is started and is based on the image you used as the base.

# When you use the COPY instruction in your Dockerfile, you're essentially copying files from your local machine into this virtual file system. 
# The specific location within the container depends on the WORKDIR instruction and the relative path specified in the COPY instruction.

# In your case, the WORKDIR /app instruction sets the working directory within the container to /app. 
# The COPY requirements.txt requirements.txt instruction copies the requirements.txt file from your local machine to the /app directory within the container.

# You don't see a physical directory on your local machine because the Docker container's file system is isolated from your host machine's file system. 
# It's a virtual environment that exists only when the container is running.

# Once you run the container, you can access the files within the container using tools like docker exec or by mounting volumes to share files between the container and your host machine.