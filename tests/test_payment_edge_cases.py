import pytest
from datetime import date, timedelta
from app.models.owner import Owner
from app.models.dog import Dog
from app.models.stay import Stay
from app.models.payment import Payment, DAILY_RATE

def test_payment_zero_duration(db_session):
    """Test payment calculation for same-day stay"""
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    dog = Dog(name="Rex", age=3, owner_id=owner.id)
    db_session.add_all([owner, dog])
    db_session.commit()
    
    today = date.today()
    stay = Stay(
        start_date=today,
        end_date=today,  # Same day
        dog_id=dog.id,
        owner_id=owner.id
    )
    db_session.add(stay)
    db_session.commit()
    
    payment = Payment(stay_id=stay.id)
    amount = payment.calculate_amount(db_session)
    
    # One day stay should cost one daily rate
    assert amount == DAILY_RATE

def test_payment_with_additional_fee(db_session):
    """Test payment calculation with additional fee per day"""
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    dog = Dog(name="Rex", age=3, owner_id=owner.id)
    db_session.add_all([owner, dog])
    db_session.commit()
    
    additional_fee = 25.0
    stay = Stay(
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        dog_id=dog.id,
        owner_id=owner.id,
        additional_fee_per_day=additional_fee
    )
    db_session.add(stay)
    db_session.commit()
    
    payment = Payment(stay_id=stay.id)
    amount = payment.calculate_amount(db_session)
    
    # 3 days * (DAILY_RATE + additional_fee)
    expected_amount = 3 * (DAILY_RATE + additional_fee)
    assert amount == expected_amount