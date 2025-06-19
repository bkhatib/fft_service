#!/bin/bash

# Stop and remove any existing container
echo "Stopping existing containers..."
docker stop fft-service || true
docker rm fft-service || true

# Remove old image
echo "Removing old image..."
docker rmi fft-service || true

# Build new image
echo "Building new image..."
docker build -t fft-service .

# Run new container
echo "Starting new container..."
docker run -d \
    --name fft-service \
    --restart always \
    -p 8000:8000 \
    --env-file .env \
    fft-service

echo "Deployment completed!"

# Show logs
docker logs -f fft-service 