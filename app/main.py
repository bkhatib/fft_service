from fastapi import FastAPI, HTTPException
from app.models import CategorizeRequest, CategorizeResponse
from app.categorizer import categorize_email

app = FastAPI(title="Email Categorization Service API")

@app.post("/categorize", response_model=CategorizeResponse)
def categorize(request: CategorizeRequest):
    try:
        result = categorize_email(request.email_subject, request.email_body)
        return CategorizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 