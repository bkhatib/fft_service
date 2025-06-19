#!/bin/bash

# Define variables
EC2_IP="51.20.73.10"
PEM_PATH="/Users/bashar.khatib/Downloads/fft_service_pem.pem"

# Create necessary directories on EC2
ssh -i "$PEM_PATH" ec2-user@"$EC2_IP" "mkdir -p ~/fft_service"

# Sync files to EC2
rsync -avz -e "ssh -i $PEM_PATH" \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude '.env' \
    ./ ec2-user@"$EC2_IP":~/fft_service/

echo "Files synced successfully to EC2!" 