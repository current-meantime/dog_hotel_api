import pytest
from datetime import date, timedelta, datetime, timezone
from app.models.owner import Owner
from app.models.dog import Dog
from app.models.stay import Stay
from app.models.payment import Payment
from app.models.bank_transfer import BankTransfer
from app.services.update_payments_from_transfers import update_payments_from_transfers

def test_exact_amount_match(db_session):
    """Test matching transfer with exact payment amount"""
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
    
    payment = Payment(stay_id=stay.id)
    payment.amount = payment.calculate_amount(db_session)
    db_session.add(payment)
    
    transfer = BankTransfer(
        from_account="123456789",
        sender_name="Test Owner",
        title=str(stay.id),
        amount=payment.amount  # Exact match
    )
    db_session.add(transfer)
    db_session.commit()
    
    update_payments_from_transfers(db_session)
    
    updated_payment = db_session.get(Payment, payment.id)
    assert updated_payment.is_paid == True
    assert updated_payment.is_overdue == False

def test_partial_payment(db_session):
    """Test matching transfer with partial payment amount"""
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
    
    payment = Payment(stay_id=stay.id)
    payment.amount = payment.calculate_amount(db_session)
    db_session.add(payment)
    
    transfer = BankTransfer(
        from_account="123456789",
        sender_name="Test Owner",
        title=str(stay.id),
        amount=payment.amount / 2  # Half payment
    )
    db_session.add(transfer)
    db_session.commit()
    
    update_payments_from_transfers(db_session)
    
    updated_payment = db_session.get(Payment, payment.id)
    assert updated_payment.is_paid == False
    assert updated_payment.is_overdue == True

def test_invalid_transfer_title(db_session):
    """Test transfer with invalid stay ID in title"""
    transfer = BankTransfer(
        from_account="123456789",
        sender_name="Test Owner",
        title="invalid_id",
        amount=100.0
    )
    db_session.add(transfer)
    db_session.commit()
    
    update_payments_from_transfers(db_session)
    
    # Transfer should remain unmatched
    updated_transfer = db_session.get(BankTransfer, transfer.id)
    assert updated_transfer.matched_payment_id is None