import os
import json
from datetime import datetime
from openai import OpenAI
import requests
from .models import CategorizeResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
INFORMATICA_API_URL = os.getenv("INFORMATICA_API_URL", "https://emw1-apigw.dm-em.informaticacloud.com/t/almosafer.prod.com/Process_Data_SF_Case_AI_Updates")
INFORMATICA_AUTH = os.getenv("INFORMATICA_AUTH", "")

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
if not INFORMATICA_AUTH:
    raise ValueError("INFORMATICA_AUTH environment variable is required")

# Priority mapping for Informatica API
PRIORITY_MAPPING = {
    4: "Critical",
    3: "High",
    2: "Medium",
    1: "Low"
}

client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT = """
You are a categorization helper who is working on an Online Travel Agency (OTA) system,
The OTA is called Almosafer or Seera Group, we are getting these emails communication from our suppliers whenever they want to inform us about something
Your Job is to categorize emails we are receiving, these emails are from our hotels rooms suppliers that we are reselling their rooms on our platform.

You need to categorize the email into one of the following categories:
* STOP_SALE: If the hotel is asking us to stop sale for a specific room type or all rooms for a specific period, or the hotel is not operational, or the hotel is not accepting any new bookings
* BOOK_OUT: If the email is about a that the hotel is fully booked and they cannot accept any more bookings
* PAYMENT_ISSUE: If the email is about any kind of issue in the payment, VCC, Tax/Municipality fees
* NO_CONTRACT: If there is no contract between us and the hotel, or the contract has been expired
* HOTEL_NON_OPERATIONAL: If the hotel is not operational, because of renovation, or any other reason
* WRONG_INFORMATION: if the email is informing us thet we are sending them wrong information (Pax No, Room Type, Bedding, Mapping, Meal Plan, Nationality, Dates, View, etc)
* REQUIRED_INFORMATION: If the email is about any information that is required from us to provide
* SANCTIONS: If the email is about sanctions or any legal issues about the traveller information, like the traveller is on a sanctions list, or the hotel is not accepting the traveller
* RATE_ISSUE: If there is any issue with the rate we are sending to them
* NOT_REACHABLE: If the email is about any issue with communication with the hotel, like the hotel is not responding to us
* REFUSED_TO_HELP: If the email is about that the hotel is refusing to help us with any issue, or they are not willing to provide us with any solution
* DUPLICITY_NOTIFICATION: If the email is about a duplicate booking
* BOOKING_CONFIRMATION_NOTIFICATION: If the email is about a confirmation of a booking
* INVOICE: If the email is an invoice from the hotel supplier
* CREDIT_NOTE: If the email is about a credit note from the supplier
* CANCELLATION_WITHOUT_NOTIFICATION: If the email is about a cancellation thet the hotel did without use or the traveller requesting it
* CANCELLATION_NOTIFICATION: If the email is about a cancellation for multiple bookings list
* ACKNOWLEDGMENT: If the email is an acknowledgment that they have received our enquiry and they will reply to us once they are done
* SURVEY_FEEDBACK: If the email is about a survey or feedback request from us
* OTHER: If non of the above one is relevant

Along with this you also need to extract the following information from the email:
Hotel Name: the name of the hotel this email about
City Name: the city name of the hotel this email about
Supplier Name: the name of the supplier this email about like HotelBeds, TBO, Expedia, ....
Check in Date: The Check in date of the booking in this email in YYYY-MM-DD format
Check out Date: The Check out date of the booking in this email in YYYY-MM-DD format
Hotel Confirmation Number (HCN): Look for numbers that are:
1. Explicitly mentioned as "HCN" or "hotel confirmation number"
2. Numbers in format XXX-XXXXXXX (like 277-2081766)
3. Numbers mentioned in context of hotel confirmation or booking reference
Agent reference ID: The reference ID of the booking, it should be a booking ID that starts with 'H2' then a sequence of numbers, eg. H2412311166652, but it is NOT this format HTL-WBD-XXXXXX
Your Category: Give me a suggested category from your side, if you will category it by yourself outside the above list
All Reference Numbers: Give me a list of strings of all reference numbers mentioned in this email

IMPORTANT NOTES:
1. For Hotel Confirmation Number (HCN):
   - If you see a number in format XXX-XXXXXXX, it's likely an HCN
   - If the subject or body mentions "HCN" followed by a number, that's the HCN
   - Even if the email is requesting an HCN, include any reference number that could be the HCN
2. For references, include ALL numbers that could be reference numbers, including:
   - Case numbers
   - HCN numbers
   - Booking references
   - Any other numerical identifiers

Respond ONLY in a valid JSON object with the following exact field names in snake_case:
category, hotel_name, city_name, supplier_name, check_in_date, check_out_date, hotel_confirmation_number, agent_reference_id, ai_category, references
- Use snake_case for all field names.
- The category must be one of the provided categories.
- If a value is missing, use null or an empty string.
"""

def days_diff(date):
    try:
        if not date:
            return -1
        check_in_date = datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.today().date()
        return (check_in_date - today).days
    except Exception:
        return -1

def detect_priority(category, hotel_confirmation_number=None):
    if category in ["STOP_SALE", "BOOK_OUT", "PAYMENT_ISSUE", "NO_CONTRACT", "HOTEL_NON_OPERATIONAL", "WRONG_INFORMATION", "REQUIRED_INFORMATION", "SANCTIONS", "RATE_ISSUE", "NOT_REACHABLE", "REFUSED_TO_HELP", "DUPLICITY_NOTIFICATION"]:
        return 4
    elif category in ["CREDIT_NOTE", "CANCELLATION_WITHOUT_NOTIFICATION"]:
        return 3
    elif category in ["ACKNOWLEDGMENT", "OTHER", "SURVEY_FEEDBACK"]:
        return 1
    elif category in ["CANCELLATION_NOTIFICATION"]:
        return 2
    elif category in ["BOOKING_CONFIRMATION_NOTIFICATION", "INVOICE", "CREDIT_NOTE"]:
        if hotel_confirmation_number:
            return 3
        else:
            return 2
    else:
        return 3

def update_case_in_informatica(case_id: str, priority: int, category: str) -> dict:
    """
    Updates case information in Informatica.
    
    Args:
        case_id (str): The Salesforce case number
        priority (int): The calculated priority (1-4)
        category (str): The AI-determined category
        
    Returns:
        dict: Response from Informatica API
        
    Raises:
        ValueError: If required fields are missing or priority is invalid
        requests.RequestException: If API call fails
    """
    if not case_id or not priority or not category:
        raise ValueError("case_id, priority, and category are required for Informatica update")
    
    if priority not in PRIORITY_MAPPING:
        raise ValueError(f"Invalid priority value: {priority}. Must be between 1 and 4.")
        
    payload = {
        "caseId": case_id,
        "priority": PRIORITY_MAPPING[priority],  # Convert numeric priority to text
        "aiTag": category
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": INFORMATICA_AUTH
    }
    
    print(f"Sending request to Informatica API with payload: {payload}")
    
    try:
        response = requests.post(
            INFORMATICA_API_URL,
            json=payload,
            headers=headers
        )
        
        print(f"Informatica API Response Status Code: {response.status_code}")
        print(f"Informatica API Response Headers: {dict(response.headers)}")
        print(f"Informatica API Response Body: {response.text}")
        
        response.raise_for_status()
        
        # Try to parse JSON response, if it fails, return raw text
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw_response": response.text, "status_code": response.status_code}
            
    except requests.RequestException as e:
        error_msg = f"Error updating Informatica: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f"\nStatus Code: {e.response.status_code}"
            error_msg += f"\nResponse Body: {e.response.text}"
        print(error_msg)
        raise

def categorize_email(subject: str, body: str, case_number: str) -> dict:
    """
    Categorizes email and updates case in Informatica.
    
    Args:
        subject (str): Email subject
        body (str): Email body
        case_number (str): Salesforce case number
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": f"Subject: {subject}\n\nBody: {body}"}
        ],
        response_format={"type": "json_object"}
    )
    output = json.loads(response.choices[0].message.content)
    print("Full LLM response:", output)

    # Defensive: check for required fields
    if "category" not in output:
        raise ValueError(f"OpenAI response missing 'category' field. Full response: {output}")

    output["priority"] = detect_priority(output["category"], output.get("hotel_confirmation_number"))
    output["days"] = days_diff(output.get("check_in_date"))
    
    # Update case in Informatica
    try:
        informatica_response = update_case_in_informatica(
            case_id=case_number,
            priority=output["priority"],
            category=output["category"]
        )
        print("Informatica API call completed:")
        print(f"- Status: {'Success' if informatica_response else 'Empty Response'}")
        print(f"- Response: {informatica_response}")
        
        # Include Informatica response in the output
        output["informatica_update"] = {
            "success": True,
            "status": informatica_response.get("Status", "Unknown"),
            "message": informatica_response.get("Message", ""),
            "raw_response": informatica_response
        }
    except Exception as e:
        error_msg = str(e)
        print(f"Failed to update Informatica: {error_msg}")
        # Include error information in the output
        output["informatica_update"] = {
            "success": False,
            "error": error_msg,
            "status": "Failed",
            "message": str(e)
        }
        
    return output 