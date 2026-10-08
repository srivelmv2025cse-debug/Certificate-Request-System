import pytest
from services.request_service import RequestService
from services.validation_service import ValidationError
from database.db import get_db_connection

def test_t6_br6_no_partial_update_on_validation_failure(test_db):
    """
    Test BR6 / Section 36 - No Partial Update:
    If validation fails:
    - create NO accepted request
    - make NO resource change
    - make NO capacity change
    - make NO successful status change
    - do not create a successful history entry
    The operation must be atomic.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]

    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    capacity_before = cursor.fetchone()["available_capacity"]

    cursor.execute("SELECT COUNT(*) AS total FROM service_requests")
    req_count_before = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM request_status_history")
    history_count_before = cursor.fetchone()["total"]
    conn.close()

    # Attempt submission with invalid input (e.g. blank name)
    with pytest.raises(ValidationError):
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="   ",  # blank name violates BR5
            phone="9876543210",
            description="Testing atomic rollback",
            reference_details="REF-ATOMIC",
            chargeable_amount=500.0,
            db_path=test_db
        )

    # Verify no partial update
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    assert cursor.fetchone()["available_capacity"] == capacity_before

    cursor.execute("SELECT COUNT(*) AS total FROM service_requests")
    assert cursor.fetchone()["total"] == req_count_before

    cursor.execute("SELECT COUNT(*) AS total FROM request_status_history")
    assert cursor.fetchone()["total"] == history_count_before
    conn.close()

def test_t1_no_duplicate_incorrect_records(test_db):
    """
    Test T1:
    Submit same request parameters consecutively.
    Each submission must generate a distinct, valid, unique request ID
    and decrement capacity by exactly 1 per valid submission.
    No duplicate reference IDs are generated.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    initial_capacity = cursor.fetchone()["available_capacity"]
    conn.close()

    # Submit first request
    req1 = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Demo Student",
        phone="9876543210",
        description="Duplicate test",
        reference_details="REF-DUP",
        chargeable_amount=999.0,
        db_path=test_db
    )

    # Submit second request with identical form fields
    req2 = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Demo Student",
        phone="9876543210",
        description="Duplicate test",
        reference_details="REF-DUP",
        chargeable_amount=999.0,
        db_path=test_db
    )

    assert req1.reference_id != req2.reference_id
    assert req1.id != req2.id

    # Verify capacity decremented by exactly 2
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    assert cursor.fetchone()["available_capacity"] == initial_capacity - 2
    conn.close()
