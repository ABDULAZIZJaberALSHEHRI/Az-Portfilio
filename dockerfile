# Use an official lightweight Python image as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system libraries and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# copy the rest of code
COPY . .

# Expose the port the flask runs on
EXPOSE 5000

# Start the app with gunicorn
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
#
