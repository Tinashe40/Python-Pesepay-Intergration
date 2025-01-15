# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by your app (optional)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev

# Copy your requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app into the container
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Run the application using Gunicorn (replace 'myproject' with your project name)
CMD ["gunicorn", "donations.wsgi:application", "--bind", "0.0.0.0:8000"]
