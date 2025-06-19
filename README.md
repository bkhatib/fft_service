# Email Categorization Service

A FastAPI service that categorizes FFT emails



## Production Deployment

### AWS EC2 Deployment

1. Connect to your EC2 instance:
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

2. Install Docker (if not already installed):
```bash
# For Amazon Linux 2
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
# Log out and back in for group changes to take effect
```

3. Clone the repository:
```bash
git clone https://github.com/bkhatib/fft_service.git
cd fft_service
```

4. Set environment variables:
```bash
# Add these to ~/.bashrc or create a .env file
export OPENAI_API_KEY="your-openai-api-key"
export INFORMATICA_AUTH="your-informatica-auth"
```

5. Run the deployment script:
```bash
./deploy.sh
```

The service will be available at `http://your-ec2-ip:8000`

### Security Considerations for EC2

1. Configure Security Group:
   - Allow inbound traffic on port 8000 only from necessary IPs
   - Allow SSH (port 22) only from your IP

2. Use AWS Secrets Manager for API keys:
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Store secrets
aws secretsmanager create-secret --name FFTService --secret-string '{"OPENAI_API_KEY":"your-key","INFORMATICA_AUTH":"your-auth"}'

# Retrieve secrets (add to deploy script)
export OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id FFTService --query SecretString --output text | jq -r .OPENAI_API_KEY)
export INFORMATICA_AUTH=$(aws secretsmanager get-secret-value --secret-id FFTService --query SecretString --output text | jq -r .INFORMATICA_AUTH)
```

### Using Docker 

1. Build the Docker image:
```bash
docker build -t fft-service .
```

2. Run the container:
```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key \
  -e INFORMATICA_AUTH=your_auth_token \
  fft-service
```

### Environment Variables Required for Deployment

- `OPENAI_API_KEY`: Your OpenAI API key
- `INFORMATICA_API_URL`: Informatica API endpoint (defaults to production URL)
- `INFORMATICA_AUTH`: Informatica authentication token
- `PORT`: Server port (defaults to 8000)
- `HOST`: Server host (defaults to 0.0.0.0)

### Health Check

The service provides a health check endpoint at `/health` that returns:
```json
{
    "status": "OK"
}
```

## API Usage

Send a POST request to `/categorize` with:
```json
{
    "casenumber": "123456",
    "email_subject": "Hotel Booking Update",
    "email_body": "Your email content here"
}
```

## Response Format

The API returns:
```json
{
    "category": "REQUIRED_INFORMATION",
    "hotel_name": "Example Hotel",
    "city_name": "Dubai",
    "supplier_name": "Hotelbeds",
    "check_in_date": "2024-03-15",
    "check_out_date": "2024-03-20",
    "hotel_confirmation_number": "HCN123456",
    "agent_reference_id": "H2412311166652",
    "references": ["H2412311166652", "HCN123456"],
    "priority": 4,
    "days": 30,
    "informatica_update": {
        "success": true,
        "status": "Success",
        "message": "Salesforce case is updated"
    }
}
```

