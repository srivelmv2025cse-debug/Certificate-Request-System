import pytest
from services.request_service import RequestService
from services.validation_service import ValidationError
from database.db import get_db_connection

def test_t3_inactive_service_s103(test_db):
    """
    Test T3 / BR2:
    Attempt submission with inactive service S103.
    Expected: Rejected. State unchanged.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]

    cursor.execute("SELECT available_capacity, status FROM resources WHERE resource_id = 'S103'")
    s103_before = cursor.fetchone()
    assert s103_before["status"] == "INACTIVE"
    cap_before = s103_before["available_capacity"]

    cursor.execute("SELECT COUNT(*) AS total FROM service_requests")
    count_before = cursor.fetchone()["total"]
    conn.close()

    # Attempt submission
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S103",
            requester_name="Test Student",
            phone="9876543210",
            description="Testing S103 inactive",
            reference_details="REF-INACTIVE",
            chargeable_amount=500.0,
            db_path=test_db
        )

    assert "The selected service is inactive." in str(exc_info.value)

    # Verify state unchanged
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity, status FROM resources WHERE resource_id = 'S103'")
    s103_after = cursor.fetchone()
    assert s103_after["available_capacity"] == cap_before
    assert s103_after["status"] == "INACTIVE"

    cursor.execute("SELECT COUNT(*) AS total FROM service_requests")
    assert cursor.fetchone()["total"] == count_before
    conn.close()

def test_t7_change_eligibility_resource_before_acceptance(test_db):
    """
    Test T7 / BR2:
    Resource or user eligibility changes immediately before acceptance
    (e.g., resource capacity becomes 0 or user becomes INACTIVE).
    Expected: Request rejected. No partial update.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]

    # Manually exhaust S102 capacity to 0 right before acceptance
    cursor.execute("UPDATE resources SET available_capacity = 0 WHERE resource_id = 'S102'")
    conn.commit()

    cursor.execute("SELECT COUNT(*) AS total FROM service_requests")
    count_before = cursor.fetchone()["total"]
    conn.close()

    # Attempt submission for S102
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S102",
            requester_name="Student With No Resource",
            phone="9876543210",
            description="Trying zero capacity resource",
            reference_details="REF-EXHAUST",
            chargeable_amount=500.0,
            db_path=test_db
        )

    assert "The selected service/resource is currently unavailable." in str(exc_info.value)

    # Verify no partial update
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S102'")
    assert cursor.fetchone()["available_capacity"] == 0

    cursor.execute("SELECT COUNT(*) AS total FROM service_requests")
    assert cursor.fetchone()["total"] == count_before
    conn.close()

def test_inactive_user_rejected(test_db):
    """
    BR2: Inactive user cannot submit a request.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'INACTIVE' WHERE username = 'user2'")
    cursor.execute("SELECT id FROM users WHERE username = 'user2'")
    user2_id = cursor.fetchone()["id"]
    conn.commit()
    conn.close()

    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user2_id,
            service_id="S101",
            requester_name="Inactive User",
            phone="9876543210",
            description="Testing inactive user",
            reference_details="REF-INACT",
            chargeable_amount=500.0,
            db_path=test_db
        )

    assert "User is inactive." in str(exc_info.value)
