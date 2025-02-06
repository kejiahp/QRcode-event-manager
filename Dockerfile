# Use the Python 3.13.1 alpine official image
# https://hub.docker.com/_/python
FROM python:3.13.1-alpine

# Create and change to the app directory.
WORKDIR /app

# Copy local code to the container image.
COPY . .

# Install project dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Run the web service on container startup.
CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
