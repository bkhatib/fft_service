# Email Categorization Service

A FastAPI service that categorizes supplier emails for Almosafer/Seera Group using OpenAI's GPT-4.

## Features

- Categorizes emails into predefined categories (STOP_SALE, PAYMENT_ISSUE, etc.)
- Extracts key information like hotel name, dates, and reference numbers
- Calculates priority levels and days to check-in
- Input validation for required fields
- Automated testing with pytest


## Production Deployment

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

