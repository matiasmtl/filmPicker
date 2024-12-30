# Use an official Python runtime as a parent image
FROM --platform=$TARGETPLATFORM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY src /app/src
COPY movies.json /app/src/movies.json

# Set permissions
RUN chmod 777 /app/src && \
    chmod 666 /app/src/movies.json

# Define environment variable
ENV FLASK_APP=src/main.py \
    MOVIES_FILE=/app/src/movies.json \
    FLASK_ENV=production \
    FLASK_DEBUG=0

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Switch to non-root user for security
RUN useradd -m myuser
USER myuser

# Run app.py when the container launches
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
