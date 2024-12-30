# Use an official Python runtime as a parent image
FROM --platform=$BUILDPLATFORM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directory and copy movies.json
RUN mkdir -p /app/src
COPY src/movies.json /app/src/

# Copy the rest of the application code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=src/main.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
