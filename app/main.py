from fastapi import FastAPI, HTTPException
from app.models import CategorizeRequest, CategorizeResponse
from app.categorizer import categorize_email

app = FastAPI(
    title="Email Categorization Service",
    description="""
    This service provides an API endpoint to categorize supplier emails for Almosafer/Seera Group using OpenAI's GPT-4.
    
    The service can:
    * Categorize emails into predefined business categories
    * Extract key information like hotel name, dates, and reference numbers
    * Calculate priority levels and days to check-in
    * Validate input fields
    
    For more information, visit our [GitHub repository](https://github.com/bkhatib/fft_service).
    """,
    version="1.0.0",
    contact={
        "name": "Almosafer/Seera Group",
        "url": "https://github.com/bkhatib/fft_service",
    },
    license_info={
        "name": "Private",
        "url": "https://github.com/bkhatib/fft_service",
    }
)

@app.post(
    "/categorize",
    response_model=CategorizeResponse,
    summary="Categorize a supplier email",
    description="""
    Analyzes the content of a supplier email and:
    * Categorizes it into predefined business categories
    * Extracts relevant information (hotel name, dates, references)
    * Calculates priority and days to check-in
    * Updates case information in Informatica
    
    The email is processed using OpenAI's GPT-4 model for accurate categorization.
    """,
    response_description="""
    Returns the categorization result including:
    * Email category (e.g., STOP_SALE, PAYMENT_ISSUE)
    * Extracted information (hotel details, dates)
    * Priority level (1-4)
    * Days to check-in
    
    Note: Also updates case information in Informatica in the background.
    """,
)
async def categorize(request: CategorizeRequest):
    """
    Categorize a supplier email and extract relevant information.
    
    Args:
        request (CategorizeRequest): The email details including case number, subject, and body
        
    Returns:
        CategorizeResponse: The categorization result with extracted information
        
    Raises:
        HTTPException: If there's an error processing the request or updating Informatica
    """
    try:
        result = categorize_email(
            subject=request.email_subject,
            body=request.email_body,
            case_number=request.casenumber
        )
        return CategorizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/health",
    summary="Health check endpoint",
    description="Returns 200 OK if the service is running",
    response_description="Simple OK message"
)
async def health_check():
    """
    Simple health check endpoint to verify the service is running.
    """
    return {"status": "OK"} 