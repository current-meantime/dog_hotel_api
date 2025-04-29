import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta

def test_create_owner(test_client):
    """Test owner creation endpoint"""
    response = test_client.post(
        "/owners/",
        json={
            "fullname": "John Doe",
            "email": "john@example.com",
            "phone_number": 123456789
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["fullname"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data

def test_create_dog(test_client):
    """Test dog creation endpoint"""
    # First create an owner
    owner_response = test_client.post(
        "/owners/",
        json={
            "fullname": "Jane Doe",
            "email": "jane@example.com",
            "phone_number": 987654321
        }
    )
    owner_id = owner_response.json()["id"]
    
    # Then create a dog
    response = test_client.post(
        "/dogs/",
        json={
            "name": "Max",
            "age": 2,
            "owner_id": owner_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Max"
    assert data["owner_id"] == owner_id

def test_create_stay_with_payment(test_client):
    """Test stay creation with automatic payment creation"""
    # Create owner and dog first
    owner_response = test_client.post(
        "/owners/",
        json={
            "fullname": "Alice Smith",
            "email": "alice@example.com",
            "phone_number": 555555555
        }
    )
    owner_id = owner_response.json()["id"]
    
    dog_response = test_client.post(
        "/dogs/",
        json={
            "name": "Luna",
            "age": 1,
            "owner_id": owner_id
        }
    )
    dog_id = dog_response.json()["id"]
    
    # Create stay
    response = test_client.post(
        "/stays/",
        json={
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=3)),
            "owner_id": owner_id,
            "dog_id": dog_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["owner_id"] == owner_id
    assert data["dog_id"] == dog_id

def test_search_stays(test_client):
    """Test stay search with filters"""
    response = test_client.get("/stays/", params={
        "status": "upcoming",
        "min_days": 2,
        "max_days": 7
    })
    assert response.status_code == 200
    
def test_invalid_stay_dates(test_client):
    """Test stay creation with invalid dates"""
    response = test_client.post(
        "/stays/",
        json={
            "start_date": str(date.today() + timedelta(days=5)),
            "end_date": str(date.today()),
            "owner_id": 1,
            "dog_id": 1
        }
    )
    assert response.status_code == 400