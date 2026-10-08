import pytest
from services.request_service import RequestService
from database.db import get_db_connection

def test_t12_change_master_data_after_request_snapshot_immutable(test_db):
    """
    Test T12 / BR3:
    When a request is submitted, save a snapshot of:
    - service ID
    - service name
    - service value
    Later changes to master service/resource data MUST NOT change the historical request information.
    """
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user1'")
    user1_id = cursor.fetchone()["id"]
    cursor.execute("SELECT service_name, capacity FROM resources WHERE resource_id = 'S101'")
    master_original = cursor.fetchone()
    original_name = master_original["service_name"]
    original_capacity = master_original["capacity"]
    conn.close()

    # Step 1: Submit request under original service master data
    req = RequestService.submit_request(
        user_id=user1_id,
        service_id="S101",
        requester_name="Snapshot Tester",
        phone="9876543210",
        description="Testing snapshot immutability",
        reference_details="REF-SNAP-01",
        chargeable_amount=500.0,
        db_path=test_db
    )

    assert req.service_name_snapshot == original_name
    assert req.service_value_snapshot == float(original_capacity)

    # Step 2: Later, Administrator changes the master resource catalog
    conn = get_db_connection(test_db)
    with conn:
        conn.execute(
            """
            UPDATE resources
            SET service_name = 'MODIFIED Certificate Request Alpha',
                capacity = 999
            WHERE resource_id = 'S101'
            """
        )
    conn.close()

    # Step 3: Verify master data was indeed changed
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT service_name, capacity FROM resources WHERE resource_id = 'S101'")
    master_new = cursor.fetchone()
    assert master_new["service_name"] == "MODIFIED Certificate Request Alpha"
    assert master_new["capacity"] == 999

    # Step 4: Retrieve the historical request and verify original snapshot is PRESERVED
    historical_req = RequestService.get_request_by_reference(req.reference_id, conn)
    assert historical_req.service_name_snapshot == original_name
    assert historical_req.service_name_snapshot != master_new["service_name"]
    assert historical_req.service_value_snapshot == float(original_capacity)
    assert historical_req.service_value_snapshot != master_new["capacity"]
    conn.close()
