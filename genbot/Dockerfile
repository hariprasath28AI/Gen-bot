FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Update package lists and install system packages
RUN apt-get update && \
    apt-get install -y curl git build-essential

# Install faiss-cpu and gunicorn
RUN pip install faiss-cpu==1.7.4 gunicorn

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 80 for the Flask application
EXPOSE 80

# Define environment variable (if needed)
# ENV NAME World

# Use Gunicorn to run your Flask application
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:80", "main:app"]
