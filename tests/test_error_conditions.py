import pytest
from fastapi.testclient import TestClient

def test_nonexistent_resources(test_client):
    """Test accessing non-existent resources"""
    endpoints = [
        "/owners/999",
        "/dogs/999",
        "/stays/999",
        "/payments/999",
        "/bank_transfers/999"
    ]
    
    for endpoint in endpoints:
        response = test_client.get(endpoint)
        assert response.status_code == 404

def test_invalid_input_types(test_client):
    """Test endpoints with invalid input types"""
    # Invalid owner creation
    response = test_client.post(
        "/owners/",
        json={
            "fullname": "Test Owner",
            "email": "invalid_email",  # Invalid email format
            "phone_number": "not_a_number"  # Should be integer
        }
    )
    assert response.status_code == 422
    
    # Invalid payment amount
    response = test_client.post(
        "/payments/",
        json={
            "stay_id": 1,
            "amount": "not_a_number",  # Should be float
            "is_paid": "not_a_boolean"  # Should be boolean
        }
    )
    assert response.status_code == 422

def test_duplicate_resources(test_client, db_session):
    """Test creating duplicate resources"""
    # Try to create owner with same email
    owner_data = {
        "fullname": "Test Owner",
        "email": "test@example.com",
        "phone_number": 123456789
    }
    
    response1 = test_client.post("/owners/", json=owner_data)
    assert response1.status_code == 200
    
    response2 = test_client.post("/owners/", json=owner_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]