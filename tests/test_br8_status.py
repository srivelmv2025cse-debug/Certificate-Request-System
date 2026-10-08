import pytest
from services.request_service import RequestService
from services.validation_service import ValidationError
from models.user import User
from database.db import get_db_connection

def test_t9_admin_valid_status_progression(test_db):
    """
    Test T9 / BR8:
    Valid sequence:
    SUBMITTED -> APPROVED/ASSIGNED -> IN_PROGRESS -> COMPLETED
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_row = cursor.fetchone()
    admin_user = User.from_row(admin_row)
    conn.close()

    # Step 1: Create SUBMITTED request
    req = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Progression Tester",
        phone="9876543210",
        description="Testing valid transitions",
        reference_details="REF-SEQ",
        chargeable_amount=500.0,
        db_path=test_db
    )
    assert req.status == "SUBMITTED"

    # Step 2: SUBMITTED -> APPROVED/ASSIGNED
    RequestService.advance_status(req.reference_id, "APPROVED/ASSIGNED", admin_user, db_path=test_db)
    conn = get_db_connection(test_db)
    updated = RequestService.get_request_by_reference(req.reference_id, conn)
    assert updated.status == "APPROVED/ASSIGNED"
    conn.close()

    # Step 3: APPROVED/ASSIGNED -> IN_PROGRESS
    RequestService.advance_status(req.reference_id, "IN_PROGRESS", admin_user, db_path=test_db)
    conn = get_db_connection(test_db)
    updated = RequestService.get_request_by_reference(req.reference_id, conn)
    assert updated.status == "IN_PROGRESS"
    conn.close()

    # Step 4: IN_PROGRESS -> COMPLETED
    RequestService.advance_status(req.reference_id, "COMPLETED", admin_user, db_path=test_db)
    conn = get_db_connection(test_db)
    updated = RequestService.get_request_by_reference(req.reference_id, conn)
    assert updated.status == "COMPLETED"

    # Check history count (1 initial SUBMITTED + 3 transitions = 4 total history rows)
    history = RequestService.get_request_history(req.reference_id, conn)
    assert len(history) == 4
    conn.close()

def test_t9_admin_skipping_stages_fails(test_db):
    """
    Test T9 / BR8:
    Skipping stages must fail:
    - SUBMITTED -> IN_PROGRESS (Invalid)
    - SUBMITTED -> COMPLETED (Invalid)
    - APPROVED/ASSIGNED -> COMPLETED (Invalid)
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
        requester_name="Skip Tester",
        phone="9876543210",
        description="Testing invalid skip",
        reference_details="REF-SKIP",
        chargeable_amount=500.0,
        db_path=test_db
    )

    # 1. Attempt SUBMITTED -> IN_PROGRESS
    with pytest.raises(ValidationError) as exc1:
        RequestService.advance_status(req.reference_id, "IN_PROGRESS", admin_user, db_path=test_db)
    assert "Invalid status transition" in str(exc1.value)

    # 2. Attempt SUBMITTED -> COMPLETED
    with pytest.raises(ValidationError) as exc2:
        RequestService.advance_status(req.reference_id, "COMPLETED", admin_user, db_path=test_db)
    assert "Invalid status transition" in str(exc2.value)

    # Move legitimately to APPROVED/ASSIGNED
    RequestService.advance_status(req.reference_id, "APPROVED/ASSIGNED", admin_user, db_path=test_db)

    # 3. Attempt APPROVED/ASSIGNED -> COMPLETED (skipping IN_PROGRESS)
    with pytest.raises(ValidationError) as exc3:
        RequestService.advance_status(req.reference_id, "COMPLETED", admin_user, db_path=test_db)
    assert "Invalid status transition" in str(exc3.value)
