import pytest
from datetime import date, datetime, timezone, timedelta
from app.models.dog import Dog
from app.models.owner import Owner
from app.models.stay import Stay
from app.models.payment import Payment
from app.models.bank_transfer import BankTransfer

def test_owner_model(db_session):
    """Test Owner model creation and relationships"""
    owner = Owner(
        fullname="Test Owner",
        email="test@example.com",
        phone_number=123456789
    )
    db_session.add(owner)
    db_session.commit()
    
    assert owner.id is not None
    assert owner.fullname == "Test Owner"
    assert owner.email == "test@example.com"
    assert owner.phone_number == 123456789

def test_dog_model_with_owner(db_session):
    """Test Dog model creation with owner relationship"""
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    db_session.add(owner)
    db_session.commit()
    
    dog = Dog(
        name="Rex",
        age=3,
        owner_id=owner.id
    )
    db_session.add(dog)
    db_session.commit()
    
    assert dog.id is not None
    assert dog.name == "Rex"
    assert dog.owner_id == owner.id
    assert dog.owner == owner

def test_stay_model_relationships(db_session):
    """Test Stay model with its relationships"""
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    db_session.add(owner)
    
    dog = Dog(name="Rex", age=3, owner_id=owner.id)
    db_session.add(dog)
    db_session.commit()
    
    stay = Stay(
        start_date=date.today(),
        end_date=date.today() + timedelta(days=5),
        dog_id=dog.id,
        owner_id=owner.id
    )
    db_session.add(stay)
    db_session.commit()
    
    assert stay.dog == dog
    assert stay.owner == owner
    assert len(stay.payments) == 0

def test_payment_calculation(db_session):
    """Test payment amount calculation"""
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    dog = Dog(name="Rex", age=3, owner_id=owner.id)
    db_session.add_all([owner, dog])
    db_session.commit()
    
    stay = Stay(
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        dog_id=dog.id,
        owner_id=owner.id
    )
    db_session.add(stay)
    db_session.commit()
    
    payment = Payment(stay_id=stay.id)
    amount = payment.calculate_amount(db_session)
    
    # 3 days * 50.0 (DAILY_RATE)
    assert amount == 150.0