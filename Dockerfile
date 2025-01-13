# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY src /app/src

# Create data directory and initialize empty JSON files
RUN mkdir -p /app/src/data && \
    echo '[]' > /app/src/data/movies.json && \
    echo '[]' > /app/src/data/tv_shows.json && \
    chmod -R 777 /app/src/data

# Set environment variables
ENV MOVIES_FILE=/app/src/data/movies.json \
    TV_SHOWS_FILE=/app/src/data/tv_shows.json \
    FLASK_APP=src/main.py \
    FLASK_ENV=production \
    FLASK_DEBUG=0

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Switch to non-root user for security
RUN useradd -m myuser
USER myuser

# Define volume for data directory specifically
VOLUME ["/app/src/data"]

# Run app.py when the container launches
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
