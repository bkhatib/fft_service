# Email Categorization Service

A FastAPI service that categorizes supplier emails for Almosafer/Seera Group using OpenAI's GPT-4.

## Features

- Categorizes emails into predefined categories (STOP_SALE, PAYMENT_ISSUE, etc.)
- Extracts key information like hotel name, dates, and reference numbers
- Calculates priority levels and days to check-in
- Input validation for required fields
- Automated testing with pytest

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd FFT_SERVICE
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `env.example` to `.env`
   - Update `.env` with your OpenAI API key and other configurations

## Running the Service

Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API documentation: http://localhost:8000/docs
- Categorization endpoint: http://localhost:8000/categorize

## Testing

Run the test suite:
```bash
pytest
```

## Security Notes

- Never commit the `.env` file or expose your API keys
- Always use environment variables for sensitive information
- Keep your dependencies updated for security patches

## API Usage

Send a POST request to `/categorize` with:
```json
{
    "casenumber": "123456",
    "email_subject": "Hotel Booking Update",
    "email_body": "Your email content here"
}
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

[Your chosen license]

---
