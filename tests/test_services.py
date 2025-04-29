import pytest
from datetime import date, datetime, timezone, timedelta
from app.services.update_dog_ages import update_dog_ages
from app.services.update_payments_from_transfers import update_payments_from_transfers
from app.models.dog import Dog
from app.models.owner import Owner
from app.models.stay import Stay
from app.models.payment import Payment
from app.models.bank_transfer import BankTransfer

def test_update_dog_ages(db_session):
    """Test automatic dog age update"""
    owner = Owner(fullname="Test Owner", email="test@example.com", phone_number=123456789)
    db_session.add(owner)
    
    # Create a dog with creation date more than a year ago
    old_date = datetime.now(timezone.utc) - timedelta(days=366)
    dog = Dog(
        name="Rex",
        age=3,
        owner_id=owner.id,
        created_at=old_date
    )
    db_session.add(dog)
    db_session.commit()
    
    update_dog_ages(db_session)
    
    updated_dog = db_session.get(Dog, dog.id)
    assert updated_dog.age == 4

def test_update_payments_from_transfers(db_session):
    """Test payment update from bank transfers"""
    # Setup test data
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
    
    payment = Payment(
        stay_id=stay.id,
        amount=150.0,
        is_paid=False
    )
    db_session.add(payment)
    
    transfer = BankTransfer(
        from_account="123456789",
        sender_name="Test Owner",
        title=str(stay.id),
        amount=150.0
    )
    db_session.add(transfer)
    db_session.commit()
    
    update_payments_from_transfers(db_session)
    
    updated_payment = db_session.get(Payment, payment.id)
    assert updated_payment.is_paid == True
    assert updated_payment.is_overdue == False