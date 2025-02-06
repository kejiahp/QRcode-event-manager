# Use the Python 3.13.1 alpine official image
# https://hub.docker.com/_/python
FROM python:3.13.1-alpine

# Create and change to the app directory.
WORKDIR /app

# Copy local code to the container image.
COPY . .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install -r requirements.txt

EXPOSE 8000

# Run the web service on container startup.
# CMD ["fastapi", "run", "--workers", "4", "app/main.py"]

CMD ["uvicorn", "app.main:application", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--workers", "4"]