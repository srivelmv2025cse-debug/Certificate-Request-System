import pytest
from services.request_service import RequestService
from services.validation_service import ValidationError
from models.user import User
from database.db import get_db_connection

def test_t8_user_cannot_access_or_cancel_another_users_request(test_db):
    """
    Test T8 / BR10:
    USER 2 attempts to cancel or modify USER 1's request.
    Expected: "Access denied." No data change.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT id FROM users WHERE username = 'user2'")
    user2_id = cursor.fetchone()["id"]
    conn.close()

    # User 1 submits a request
    req1 = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="User One",
        phone="9876543210",
        description="User 1 certificate request",
        reference_details="REF-U1",
        chargeable_amount=500.0,
        db_path=test_db
    )

    # User 2 attempts to cancel User 1's request
    with pytest.raises(ValidationError) as exc_info:
        RequestService.cancel_request(req1.reference_id, user2_id, db_path=test_db)

    assert "Access denied." in str(exc_info.value)

    # Verify status remains SUBMITTED
    conn = get_db_connection(test_db)
    current_req = RequestService.get_request_by_reference(req1.reference_id, conn)
    assert current_req.status == "SUBMITTED"
    conn.close()

def test_t8_user_cannot_perform_admin_actions(test_db):
    """
    Test T8 / BR10:
    Normal USER attempts to perform administrator status transitions.
    Expected: "Access denied."
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT * FROM users WHERE username = 'user1'")
    user1_obj = User.from_row(cursor.fetchone())
    conn.close()

    req = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="User One",
        phone="9876543210",
        description="Testing unauthorized admin action",
        reference_details="REF-U1-ADM",
        chargeable_amount=500.0,
        db_path=test_db
    )

    # User 1 tries to approve the request
    with pytest.raises(ValidationError) as exc_info:
        RequestService.advance_status(req.reference_id, "APPROVED/ASSIGNED", user1_obj, db_path=test_db)

    assert "Access denied." in str(exc_info.value)

    # Status remains unchanged
    conn = get_db_connection(test_db)
    current_req = RequestService.get_request_by_reference(req.reference_id, conn)
    assert current_req.status == "SUBMITTED"
    conn.close()

def test_t8_route_access_control(client, test_db):
    """
    Test web route access control via Flask test client:
    - User cannot access admin dashboard -> 403 Access denied
    - Unauthenticated user redirected to login
    - User 2 cannot view User 1's request detail route -> 403 Access denied
    """
    # 1. Unauthenticated request to admin dashboard -> redirect to login
    res_unauth = client.get("/admin/dashboard")
    assert res_unauth.status_code == 302
    assert "/login" in res_unauth.headers["Location"]

    # 2. Login as user1
    client.post("/login", data={"username": "user1", "password": "user123"})

    # User1 attempts to access admin dashboard -> 403
    res_forbidden = client.get("/admin/dashboard")
    assert res_forbidden.status_code == 403
    assert b"Access denied." in res_forbidden.data

    # User1 creates a request
    res_create = client.post("/user/create-request", data={
        "service_id": "S101",
        "requester_name": "Student One",
        "phone": "9876543210",
        "description": "Access control test",
        "reference_details": "REF-AC-01",
        "chargeable_amount": "999"
    }, follow_redirects=True)
    assert res_create.status_code == 200

    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT reference_id FROM service_requests ORDER BY id DESC LIMIT 1")
    user1_req_ref = cursor.fetchone()["reference_id"]
    conn.close()

    # Logout user1
    client.get("/logout")

    # Login as user2
    client.post("/login", data={"username": "user2", "password": "user123"})

    # User2 attempts to view User1's request details -> 403
    res_user2_cross = client.get(f"/user/requests/{user1_req_ref}")
    assert res_user2_cross.status_code == 403
    assert b"Access denied." in res_user2_cross.data
