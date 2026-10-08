import pytest
from services.request_service import RequestService
from services.validation_service import ValidationError
from models.user import User
from database.db import get_db_connection

def test_t10_cancellation_and_repeated_cancellation(test_db):
    """
    Test T10 / BR9:
    Cancel eligible request and repeat cancellation.
    Expected:
    First cancellation works.
    Resource released once.
    Second cancellation has no additional effect, shows:
    "Request has already been cancelled."
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    initial_capacity = cursor.fetchone()["available_capacity"]
    conn.close()

    # Step 1: Submit request
    req = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Cancel Candidate",
        phone="9876543210",
        description="Testing cancellation",
        reference_details="REF-CAN-01",
        chargeable_amount=500.0,
        db_path=test_db
    )

    # Capacity should have decreased by 1
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    assert cursor.fetchone()["available_capacity"] == initial_capacity - 1
    conn.close()

    # Step 2: First cancellation -> SUCCESS
    success = RequestService.cancel_request(req.reference_id, user1_id, db_path=test_db)
    assert success is True

    # Check status is CANCELLED
    conn = get_db_connection(test_db)
    cancelled_req = RequestService.get_request_by_reference(req.reference_id, conn)
    assert cancelled_req.status == "CANCELLED"
    conn.close()

    # Verify resource released EXACTLY ONCE
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    capacity_after_first_cancel = cursor.fetchone()["available_capacity"]
    assert capacity_after_first_cancel == initial_capacity
    conn.close()

    # Step 3: Repeated cancellation attempt -> MUST FAIL with clear message
    with pytest.raises(ValidationError) as exc_info:
        RequestService.cancel_request(req.reference_id, user1_id, db_path=test_db)

    assert "Request has already been cancelled." in str(exc_info.value)

    # Verify capacity has NOT increased twice
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    assert cursor.fetchone()["available_capacity"] == initial_capacity
    conn.close()

def test_cannot_cancel_non_submitted_request(test_db):
    """
    BR9: User can cancel ONLY a SUBMITTED request.
    If request is already APPROVED/ASSIGNED or IN_PROGRESS, cancellation must fail:
    "Only SUBMITTED requests can be cancelled."
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_user = User.from_row(cursor.fetchone())
    conn.close()

    req = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Approved User",
        phone="9876543210",
        description="Testing cancel after approved",
        reference_details="REF-APP-01",
        chargeable_amount=500.0,
        db_path=test_db
    )

    # Admin advances status to APPROVED/ASSIGNED
    RequestService.advance_status(req.reference_id, "APPROVED/ASSIGNED", admin_user, db_path=test_db)

    # User attempts cancellation
    with pytest.raises(ValidationError) as exc_info:
        RequestService.cancel_request(req.reference_id, user1_id, db_path=test_db)

    assert "Only SUBMITTED requests can be cancelled." in str(exc_info.value)
