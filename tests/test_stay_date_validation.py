import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.models.owner import Owner
from app.models.dog import Dog

def test_stay_end_before_start(test_client, db_session):
    """Test creating stay with end date before start date"""
    # Create test owner and dog
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    db_session.add(owner)
    db_session.commit()
    
    dog = Dog(name="Rex", age=3, owner_id=owner.id)
    db_session.add(dog)
    db_session.commit()
    
    response = test_client.post(
        "/stays/",
        json={
            "start_date": str(date.today() + timedelta(days=5)),
            "end_date": str(date.today()),
            "owner_id": owner.id,
            "dog_id": dog.id
        }
    )
    
    assert response.status_code == 400
    assert "End date cannot be earlier than start date" in response.json()["detail"]

def test_overlapping_stays(test_client, db_session):
    """Test creating overlapping stays for the same dog"""
    # Create test owner and dog
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    db_session.add(owner)
    db_session.commit()
    
    dog = Dog(name="Rex", age=3, owner_id=owner.id)
    db_session.add(dog)
    db_session.commit()
    
    # Create first stay
    response1 = test_client.post(
        "/stays/",
        json={
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=5)),
            "owner_id": owner.id,
            "dog_id": dog.id
        }
    )
    assert response1.status_code == 200
    
    # Try to create overlapping stay
    response2 = test_client.post(
        "/stays/",
        json={
            "start_date": str(date.today() + timedelta(days=3)),
            "end_date": str(date.today() + timedelta(days=7)),
            "owner_id": owner.id,
            "dog_id": dog.id
        }
    )
    
    assert response2.status_code == 400
    assert "Overlapping stay exists" in response2.json()["detail"]