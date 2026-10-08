import pytest
from services.request_service import RequestService
from services.validation_service import ValidationError
from database.db import get_db_connection

def test_t2_active_request_limit_4_5_6(test_db):
    """
    Test T2 / BR1:
    A user can have at most 5 active requests.
    Active requests: requests that are not COMPLETED and not CANCELLED.
    Counts 4 and 5 must be accepted.
    A 6th active request MUST be rejected with error:
    "Active request limit exceeded. A user can have at most 5 active requests."
    No database state should change after rejection.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    conn.close()

    # Submit 1st to 4th requests
    for i in range(1, 5):
        req = RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name=f"Student Req {i}",
            phone="9876543210",
            description=f"Academic purpose {i}",
            reference_details=f"REF-00{i}",
            chargeable_amount=500.0,
            db_path=test_db
        )
        assert req is not None
        assert req.status == "SUBMITTED"

    # Verify 4 requests exist and are active
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS c FROM service_requests WHERE user_id = ? AND status NOT IN ('COMPLETED', 'CANCELLED')", (user1_id,))
    assert cursor.fetchone()["c"] == 4

    # Submit 5th request -> Must be accepted
    req5 = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Student Req 5",
        phone="9876543210",
        description="Academic purpose 5",
        reference_details="REF-005",
        chargeable_amount=500.0,
        db_path=test_db
    )
    assert req5 is not None

    cursor.execute("SELECT COUNT(*) AS c FROM service_requests WHERE user_id = ? AND status NOT IN ('COMPLETED', 'CANCELLED')", (user1_id,))
    assert cursor.fetchone()["c"] == 5

    # Check resource capacity before 6th request attempt
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    capacity_before = cursor.fetchone()["available_capacity"]
    cursor.execute("SELECT COUNT(*) AS c FROM service_requests")
    requests_count_before = cursor.fetchone()["c"]
    conn.close()

    # Attempt 6th active request -> Must be REJECTED
    with pytest.raises(ValidationError) as exc_info:
        RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name="Student Req 6",
            phone="9876543210",
            description="Academic purpose 6",
            reference_details="REF-006",
            chargeable_amount=500.0,
            db_path=test_db
        )

    assert "Active request limit exceeded. A user can have at most 5 active requests." in str(exc_info.value)

    # Verify no database state changed
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    assert cursor.fetchone()["available_capacity"] == capacity_before

    cursor.execute("SELECT COUNT(*) AS c FROM service_requests")
    assert cursor.fetchone()["c"] == requests_count_before
    conn.close()

def test_completed_and_cancelled_do_not_count_toward_active_limit(test_db):
    """
    Verify completed and cancelled requests do not count toward the active limit.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    conn.close()

    # Create 5 requests
    refs = []
    for i in range(5):
        r = RequestService.submit_request(
            user_id=user1_id,
            service_id="S101",
            requester_name=f"User {i}",
            phone="9876543210",
            description=f"Desc {i}",
            reference_details=f"REF-{i}",
            chargeable_amount=1000.0,
            db_path=test_db
        )
        refs.append(r.reference_id)

    # Cancel one request
    RequestService.cancel_request(refs[0], user1_id, db_path=test_db)

    # Now active count is 4 -> 6th submission attempt (total 6th created) should succeed
    r6 = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="New User 6",
        phone="9876543210",
        description="New Desc 6",
        reference_details="REF-NEW",
        chargeable_amount=1000.0,
        db_path=test_db
    )
    assert r6 is not None
    assert r6.status == "SUBMITTED"
