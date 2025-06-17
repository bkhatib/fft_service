from pydantic import BaseModel, Field, constr, field_validator
from typing import List, Literal, Optional, Dict, Any

class CategorizeRequest(BaseModel):
    casenumber: constr(min_length=1) = Field(..., description="Salesforce case number")
    email_subject: constr(min_length=1) = Field(..., description="Email subject")
    email_body: constr(min_length=1) = Field(..., description="Email body")

    @field_validator('casenumber', 'email_subject', 'email_body')
    @classmethod
    def not_whitespace(cls, v):
        if v.strip() == "":
            raise ValueError("must not be empty or whitespace")
        return v

class CategorizeResponse(BaseModel):
    category: Literal[
        "STOP_SALE","BOOK_OUT","PAYMENT_ISSUE","NO_CONTRACT","HOTEL_NON_OPERATIONAL","RATE_ISSUE","NOT_REACHABLE","REFUSED_TO_HELP","BOOKING_CONFIRMATION_NOTIFICATION","INVOICE","CREDIT_NOTE","WRONG_INFORMATION","DUPLICITY_NOTIFICATION","REQUIRED_INFORMATION", "CANCELLATION_WITHOUT_NOTIFICATION","CANCELLATION_NOTIFICATION","SANCTIONS","ACKNOWLEDGMENT","SURVEY_FEEDBACK","OTHER"
    ]
    hotel_name: Optional[str]
    city_name: Optional[str]
    supplier_name: Optional[str]
    check_in_date: Optional[str]
    check_out_date: Optional[str]
    hotel_confirmation_number: Optional[str]
    agent_reference_id: Optional[str]
    ai_category: Optional[str]
    references: List[str]
    priority: int
    days: int
    informatica_update: Dict[str, Any] = Field(
        default_factory=dict,
        description="Response from Informatica API including status and message"
    ) 