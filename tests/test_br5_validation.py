import pytest
from services.validation_service import ValidationService, ValidationError
from services.request_service import RequestService
from database.db import get_db_connection

def test_t6_blank_name_rejected(test_db):
    """
    Test T6 / BR5:
    Name cannot be blank. Show error: "Name cannot be blank."
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    conn.close()

    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="",
            phone="9876543210",
            description="Valid description",
            reference_details="REF-001",
            chargeable_amount=500.0,
            db_path=test_db
        )
    assert "Name cannot be blank." in str(exc_info.value)

def test_t6_invalid_phone_rejected(test_db):
    """
    Test T6 / BR5:
    Phone must be exactly 10 digits.
    Show error: "Phone number must contain exactly 10 digits."
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    conn.close()

    # Case: Short phone (e.g. 123)
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="Test Student",
            phone="123",
            description="Valid description",
            reference_details="REF-001",
            chargeable_amount=500.0,
            db_path=test_db
        )
    assert "Phone number must contain exactly 10 digits." in str(exc_info.value)

    # Case: Letters in phone
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="Test Student",
            phone="98765abcd0",
            description="Valid description",
            reference_details="REF-001",
            chargeable_amount=500.0,
            db_path=test_db
        )
    assert "Phone number must contain exactly 10 digits." in str(exc_info.value)

    # Case: 11 digits
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="Test Student",
            phone="98765432101",
            description="Valid description",
            reference_details="REF-001",
            chargeable_amount=500.0,
            db_path=test_db
        )
    assert "Phone number must contain exactly 10 digits." in str(exc_info.value)

def test_t6_missing_description_and_reference(test_db):
    """
    Test T6 / BR5:
    Description and reference details cannot be blank.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    conn.close()

    # Empty description
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="Test Student",
            phone="9876543210",
            description="",
            reference_details="REF-001",
            chargeable_amount=500.0,
            db_path=test_db
        )
    assert "Description cannot be blank." in str(exc_info.value)

    # Empty reference details
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="Test Student",
            phone="9876543210",
            description="Valid description",
            reference_details="",
            chargeable_amount=500.0,
            db_path=test_db
        )
    assert "Reference details cannot be blank." in str(exc_info.value)
