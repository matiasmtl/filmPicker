# Use an official Python runtime as a parent image
FROM --platform=$TARGETPLATFORM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directory with proper permissions
RUN mkdir -p /app/src && chmod 777 /app/src

# Copy movies.json first and set permissions
COPY src/movies.json /app/src/
RUN chmod 666 /app/src/movies.json

# Copy the rest of the application code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=src/main.py
ENV MOVIES_FILE=/app/src/movies.json
ENV FLASK_DEBUG=1

# Switch to non-root user for security
RUN useradd -m myuser
USER myuser

# Run app.py when the container launches
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
