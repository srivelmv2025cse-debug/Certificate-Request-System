import pytest
import sqlite3
from services.request_service import RequestService
from models.user import User
from database.db import get_db_connection

def test_t5_complete_valid_submission_atomic_success(test_db):
    """
    Test T5 / FR1, FR3, FR4, FR5, BR7:
    Complete valid submission.
    Expected: Successful request created atomically with snapshot,
    allocated resource decrement, and status history entry.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    cap_before = cursor.fetchone()["available_capacity"]
    conn.close()

    # Submit valid request with amount 999 -> charge should be 50.0
    req = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Demo Student",
        phone="9876543210",
        description="Certificate request for academic purpose",
        reference_details="CERT-DEMO-001",
        chargeable_amount=999.0,
        db_path=test_db
    )

    assert req is not None
    assert req.reference_id.startswith("REQ-")
    assert req.status == "SUBMITTED"
    assert req.charge == 50.0
    assert req.service_name_snapshot == "Certificate Request A"
    assert req.service_value_snapshot == 10.0

    # Verify resource decremented by 1
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S101'")
    assert cursor.fetchone()["available_capacity"] == cap_before - 1

    # Verify audit history record created
    history = RequestService.get_request_history(req.reference_id, conn)
    assert len(history) == 1
    assert history[0]["new_status"] == "SUBMITTED"
    conn.close()

def test_t11_database_persistence_after_application_restart(test_db):
    """
    Test T11 / FR10:
    Simulate application restart after submission.
    Verify request, status, and resource state persist accurately in SQLite.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    conn.close()

    # 1. Create a request
    req = RequestService.submit_request(
        user_id=user1_id,
        service_id="S102",
        requester_name="Persistence Tester",
        phone="9876543210",
        description="Testing persistence across restarts",
        reference_details="REF-PERSIST-01",
        chargeable_amount=1200.0,
        db_path=test_db
    )
    ref_id = req.reference_id

    # 2. Simulate complete restart by opening a brand new SQLite connection from disk
    new_conn = sqlite3.connect(test_db)
    new_conn.row_factory = sqlite3.Row
    cur = new_conn.cursor()

    cur.execute("SELECT * FROM service_requests WHERE reference_id = ?", (ref_id,))
    persisted_req = cur.fetchone()
    assert persisted_req is not None
    assert persisted_req["reference_id"] == ref_id
    assert persisted_req["status"] == "SUBMITTED"
    assert persisted_req["charge"] == 0.0  # >= 1000 threshold
    assert persisted_req["service_name_snapshot"] == "Certificate Request B"

    # Verify resource state persisted
    cur.execute("SELECT available_capacity FROM resources WHERE resource_id = 'S102'")
    assert cur.fetchone()["available_capacity"] == 4  # Initial 5 minus 1

    # Verify status history persisted
    cur.execute("SELECT * FROM request_status_history WHERE reference_id = ?", (ref_id,))
    history_row = cur.fetchone()
    assert history_row is not None
    assert history_row["new_status"] == "SUBMITTED"

    new_conn.close()

def test_complete_demo_workflow_end_to_end(client, test_db):
    """
    Simulates Section 34 Complete Viva Demonstration Workflow:
    Step 1: Login as user1
    Step 2: Create request S101, Name: Demo Student, Phone: 9876543210,
            Description: Academic purpose, Ref: CERT-DEMO-001, Amount: 999
    Step 4: System calculates Charge = Rs.50
    Step 5: Submit -> SUBMITTED
    Step 6: View request
    Step 7: Logout
    Step 8: Login as admin
    Step 9: Open request
    Step 10: Approve/Assign
    Step 11: Move to IN_PROGRESS
    Step 12: Complete
    Step 13: Show status history
    """
    # Step 1: Login as user1
    resp = client.post("/login", data={"username": "user1", "password": "user123"}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Welcome back, Student One!" in resp.data

    # Step 2-5: Create request with amount 999 (BR4: charge = Rs.50)
    resp = client.post("/user/create-request", data={
        "service_id": "S101",
        "requester_name": "Demo Student",
        "phone": "9876543210",
        "description": "Certificate request for academic purpose",
        "reference_details": "CERT-DEMO-001",
        "chargeable_amount": "999"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Certificate request submitted successfully" in resp.data

    # Fetch reference ID
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT reference_id FROM service_requests WHERE reference_details = 'CERT-DEMO-001'")
    req_ref = cursor.fetchone()["reference_id"]
    conn.close()

    # Step 6: View request
    resp = client.get(f"/user/requests/{req_ref}")
    assert resp.status_code == 200
    assert b"Demo Student" in resp.data
    assert b"Rs. 50.00" in resp.data

    # Step 7: Logout
    client.get("/logout")

    # Step 8: Login as admin
    resp = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Administrator Control Center" in resp.data

    # Step 9-10: Open request & Approve/Assign
    resp = client.post(f"/admin/requests/{req_ref}/status", data={
        "next_status": "APPROVED/ASSIGNED"
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Step 11: Move to IN_PROGRESS
    resp = client.post(f"/admin/requests/{req_ref}/status", data={
        "next_status": "IN_PROGRESS"
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Step 12: Complete
    resp = client.post(f"/admin/requests/{req_ref}/status", data={
        "next_status": "COMPLETED"
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Step 13: View details and verify status history has all 4 states
    resp = client.get(f"/admin/requests/{req_ref}")
    assert resp.status_code == 200
    assert b"COMPLETED" in resp.data
    assert b"APPROVED/ASSIGNED" in resp.data
    assert b"IN_PROGRESS" in resp.data
