import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Mocking categorize_email for predictable results (monkeypatch in pytest)
def mock_categorize_email(subject, body):
    if "stop sales" in subject.lower():
        return {
            "category": "STOP_SALE",
            "hotel_name": "S19 Hotel Al Jaddaf",
            "city_name": "Dubai",
            "supplier_name": "TBOHolidays",
            "check_in_date": "2025-05-21",
            "check_out_date": "2025-05-22",
            "hotel_confirmation_number": "123ABC",
            "agent_reference_id": "H2412311166652",
            "ai_category": "STOP_SALE",
            "references": ["H2412311166652"],
            "priority": 4,
            "days": 365
        }
    if "payment issue" in subject.lower():
        return {
            "category": "PAYMENT_ISSUE",
            "hotel_name": "Grand Hotel",
            "city_name": "Dubai",
            "supplier_name": "Expedia",
            "check_in_date": "2025-06-01",
            "check_out_date": "2025-06-05",
            "hotel_confirmation_number": "456DEF",
            "agent_reference_id": "H2412311166652",
            "ai_category": "PAYMENT_ISSUE",
            "references": ["H2412311166652"],
            "priority": 4,
            "days": 10
        }
    if "duplicate" in subject.lower():
        return {
            "category": "DUPLICITY_NOTIFICATION",
            "hotel_name": "",
            "city_name": "",
            "supplier_name": "",
            "check_in_date": "",
            "check_out_date": "",
            "hotel_confirmation_number": "",
            "agent_reference_id": "",
            "ai_category": "DUPLICITY_NOTIFICATION",
            "references": ["H2412311166652", "H2412311166653"],
            "priority": 4,
            "days": -1
        }
    return {
        "category": "OTHER",
        "hotel_name": "",
        "city_name": "",
        "supplier_name": "",
        "check_in_date": "",
        "check_out_date": "",
        "hotel_confirmation_number": "",
        "agent_reference_id": "",
        "ai_category": "OTHER",
        "references": [],
        "priority": 3,
        "days": -1
    }

@pytest.fixture(autouse=True)
def patch_categorizer(monkeypatch):
    from app import main
    monkeypatch.setattr(main, "categorize_email", mock_categorize_email)


def test_stop_sale():
    resp = client.post("/categorize", json={
        "casenumber": "CASE001",
        "email_subject": "Urgent Stop Sales- S19 Hotel Al Jaddaf",
        "email_body": "Please stop sales for S19 Hotel Al Jaddaf from 2025-05-21 to 2025-05-22 due to renovation."
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "STOP_SALE"
    assert data["hotel_name"] == "S19 Hotel Al Jaddaf"
    assert data["priority"] == 4


def test_payment_issue():
    resp = client.post("/categorize", json={
        "casenumber": "CASE002",
        "email_subject": "Payment Issue for Booking H2412311166652",
        "email_body": "We have not received payment for booking H2412311166652 at Grand Hotel, Dubai. Please check."
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "PAYMENT_ISSUE"
    assert data["agent_reference_id"] == "H2412311166652"


def test_duplicate_booking():
    resp = client.post("/categorize", json={
        "casenumber": "CASE004",
        "email_subject": "Duplicate Booking Notification",
        "email_body": "Bookings H2412311166652 and H2412311166653 are duplicates. Please cancel one."
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "DUPLICITY_NOTIFICATION"
    assert "H2412311166652" in data["references"]
    assert "H2412311166653" in data["references"]


def test_empty_fields():
    resp = client.post("/categorize", json={
        "casenumber": "CASE003",
        "email_subject": "",
        "email_body": ""
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["category"] == "OTHER"


def test_missing_required_field():
    resp = client.post("/categorize", json={
        "email_subject": "No casenumber",
        "email_body": "Test"
    })
    assert resp.status_code == 422


def test_malformed_json():
    # Simulate malformed JSON by sending text instead of JSON
    resp = client.post("/categorize", data="not a json")
    assert resp.status_code in (400, 422) 