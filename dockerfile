# Use the official Python base image
FROM python:3.11-slim

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PORT=8080

# Create and set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and templates into the container
COPY app.py .
COPY templates/ templates/

# Ensure the directories for uploads and output exist
RUN mkdir -p uploads output

# Expose the port Flask runs on
EXPOSE 8080

# Run the Flask application
CMD ["flask", "run"]

