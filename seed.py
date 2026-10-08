import os
from database.db import get_db_connection, init_db
from config import Config

def seed_database(db_path=None, include_sample_requests=True):
    """
    Initializes database schema and populates sample demonstration data.
    Safe to run repeatedly (uses INSERT OR REPLACE / ON CONFLICT).
    """
    if db_path is None:
        db_path = Config.DATABASE_PATH

    # Initialize tables if not existing
    init_db(db_path)
    conn = get_db_connection(db_path)

    try:
        with conn:
            cursor = conn.cursor()

            # Seed 3 required demo accounts (2 USER, 1 ADMINISTRATOR)
            users = [
                ("Student One", "user1", "user123", "USER", "ACTIVE"),
                ("Student Two", "user2", "user123", "USER", "ACTIVE"),
                ("System Administrator", "admin", "admin123", "ADMINISTRATOR", "ACTIVE")
            ]

            for name, username, password, role, status in users:
                cursor.execute(
                    """
                    INSERT INTO users (name, username, password, role, status)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET
                        name=excluded.name,
                        password=excluded.password,
                        role=excluded.role,
                        status=excluded.status
                    """,
                    (name, username, password, role, status)
                )

            # Get user IDs
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_id = cursor.fetchone()["id"]
            cursor.execute("SELECT id FROM users WHERE username = 'user1'")
            user1_id = cursor.fetchone()["id"]
            cursor.execute("SELECT id FROM users WHERE username = 'user2'")
            user2_id = cursor.fetchone()["id"]

            # Set available capacity matching active request reservations
            # S101 has 5 active reservations (out of 10) -> 5 available
            # S102 has 1 active reservation (out of 5) -> 4 available
            s101_avail = 5 if include_sample_requests else 10
            s102_avail = 4 if include_sample_requests else 5

            # Seed 3 required demonstration resources
            # S101: Certificate Request A, Capacity / Value: 10, Status: ACTIVE
            # S102: Certificate Request B, Capacity / Value: 5, Status: ACTIVE
            # S103: Certificate Request C, Capacity / Value: 0, Status: INACTIVE
            resources = [
                ("S101", "Certificate Request A", 10, s101_avail, "ACTIVE", admin_id),
                ("S102", "Certificate Request B", 5, s102_avail, "ACTIVE", admin_id),
                ("S103", "Certificate Request C", 0, 0, "INACTIVE", admin_id)
            ]

            for resource_id, service_name, cap, avail_cap, status, owner_id in resources:
                cursor.execute(
                    """
                    INSERT INTO resources (resource_id, service_name, capacity, available_capacity, status, owner_user_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(resource_id) DO UPDATE SET
                        service_name=excluded.service_name,
                        capacity=excluded.capacity,
                        available_capacity=excluded.available_capacity,
                        status=excluded.status,
                        owner_user_id=excluded.owner_user_id
                    """,
                    (resource_id, service_name, cap, avail_cap, status, owner_id)
                )

            if include_sample_requests:
                # 12 Realistic Academic Certificate Demonstration Requests
                sample_requests = [
                    # USER 1 Requests
                    (
                        "REQ-20261008-0001", user1_id, "S101", "Certificate Request A", 10.0,
                        "Kavitha R", "9876543210",
                        "Bona fide certificate required for National Merit Scholarship application",
                        "717721CS104-SCHOLARSHIP", 50.0, "SUBMITTED", "S101", None
                    ),
                    (
                        "REQ-20261008-0002", user1_id, "S101", "Certificate Request A", 10.0,
                        "Kavitha R", "9876543210",
                        "Medium of Instruction (English) certificate for German University MS Application",
                        "717721CS104-MOI-GERMANY", 0.0, "APPROVED/ASSIGNED", "S101", None
                    ),
                    (
                        "REQ-20261008-0003", user1_id, "S102", "Certificate Request B", 5.0,
                        "Kavitha R", "9876543210",
                        "Course completion provisional certificate for campus placement verification",
                        "717721CS104-CAMPUS-OFFER", 0.0, "IN_PROGRESS", "S102", None
                    ),
                    (
                        "REQ-20261008-0004", user1_id, "S102", "Certificate Request B", 5.0,
                        "Kavitha R", "9876543210",
                        "Conduct and Character Certificate for TCS Digital joining formalities",
                        "717721CS104-TCS-ONBOARD", 0.0, "COMPLETED", "S102", None
                    ),
                    (
                        "REQ-20261008-0005", user1_id, "S101", "Certificate Request A", 10.0,
                        "Kavitha R", "9876543210",
                        "Duplicate hall ticket request for Nov/Dec End Semester arrear exam",
                        "717721CS104-DHT-ARREAR", 50.0, "CANCELLED", "S101", "2026-10-08 10:15:00"
                    ),
                    (
                        "REQ-20261008-0012", user1_id, "S101", "Certificate Request A", 10.0,
                        "Kavitha R", "9876543210",
                        "Bona fide certificate for Tatkal Passport Application at Regional Passport Office",
                        "717721CS104-PASSPORT-RPO", 50.0, "COMPLETED", "S101", None
                    ),

                    # USER 2 Requests
                    (
                        "REQ-20261008-0006", user2_id, "S101", "Certificate Request A", 10.0,
                        "Arun Kumar S", "9443218765",
                        "Bona fide certificate for Canara Bank Vidyasri Education Loan subsidy scheme",
                        "717721EC042-CANARA-LOAN", 50.0, "SUBMITTED", "S101", None
                    ),
                    (
                        "REQ-20261008-0007", user2_id, "S101", "Certificate Request A", 10.0,
                        "Arun Kumar S", "9443218765",
                        "CGPA to Percentage Conversion Certificate for TNPSC Assistant Engineer Exam",
                        "717721EC042-TNPSC-AE", 0.0, "APPROVED/ASSIGNED", "S101", None
                    ),
                    (
                        "REQ-20261008-0008", user2_id, "S102", "Certificate Request B", 5.0,
                        "Arun Kumar S", "9443218765",
                        "Industrial Internship NOC Letter for Bosch Global Software Technologies Bangalore",
                        "717721EC042-BOSCH-NOC", 50.0, "COMPLETED", "S102", None
                    ),
                    (
                        "REQ-20261008-0009", user2_id, "S101", "Certificate Request A", 10.0,
                        "Arun Kumar S", "9443218765",
                        "Official transcript verification letter for University of Texas Dallas",
                        "717721EC042-UTD-MS", 50.0, "CANCELLED", "S101", "2026-10-08 11:20:00"
                    ),
                    (
                        "REQ-20261008-0010", user2_id, "S101", "Certificate Request A", 10.0,
                        "Arun Kumar S", "9443218765",
                        "Tuition Fee Structure Verification Certificate for SBI Scholar Loan",
                        "717721EC042-SBI-SCHOLAR", 0.0, "IN_PROGRESS", "S101", None
                    ),
                    (
                        "REQ-20261008-0011", user2_id, "S102", "Certificate Request B", 5.0,
                        "Arun Kumar S", "9443218765",
                        "Anna University Zonal Badminton Tournament Participation Endorsement",
                        "717721EC042-SPORTS-ZONAL", 50.0, "COMPLETED", "S102", None
                    )
                ]

                for (ref, uid, sid, sname, sval, rname, phone, desc, rdetail, charge, status, resid, ctime) in sample_requests:
                    cursor.execute(
                        """
                        INSERT INTO service_requests (
                            reference_id, user_id, service_id, service_name_snapshot,
                            service_value_snapshot, requester_name, phone, description,
                            reference_details, charge, status, resource_id, created_at, updated_at, cancelled_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
                        ON CONFLICT(reference_id) DO UPDATE SET
                            requester_name=excluded.requester_name,
                            description=excluded.description,
                            reference_details=excluded.reference_details,
                            status=excluded.status,
                            charge=excluded.charge,
                            cancelled_at=excluded.cancelled_at
                        """,
                        (ref, uid, sid, sname, sval, rname, phone, desc, rdetail, charge, status, resid, ctime)
                    )

                # Reset and seed complete audit history trail for demonstration
                cursor.execute("DELETE FROM request_status_history")
                histories = [
                    # REQ-0001 (SUBMITTED)
                    ("REQ-20261008-0001", user1_id, "NONE", "SUBMITTED"),

                    # REQ-0002 (APPROVED/ASSIGNED)
                    ("REQ-20261008-0002", user1_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0002", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),

                    # REQ-0003 (IN_PROGRESS)
                    ("REQ-20261008-0003", user1_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0003", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),
                    ("REQ-20261008-0003", admin_id, "APPROVED/ASSIGNED", "IN_PROGRESS"),

                    # REQ-0004 (COMPLETED)
                    ("REQ-20261008-0004", user1_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0004", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),
                    ("REQ-20261008-0004", admin_id, "APPROVED/ASSIGNED", "IN_PROGRESS"),
                    ("REQ-20261008-0004", admin_id, "IN_PROGRESS", "COMPLETED"),

                    # REQ-0005 (CANCELLED)
                    ("REQ-20261008-0005", user1_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0005", user1_id, "SUBMITTED", "CANCELLED"),

                    # REQ-0012 (COMPLETED)
                    ("REQ-20261008-0012", user1_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0012", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),
                    ("REQ-20261008-0012", admin_id, "APPROVED/ASSIGNED", "IN_PROGRESS"),
                    ("REQ-20261008-0012", admin_id, "IN_PROGRESS", "COMPLETED"),

                    # REQ-0006 (SUBMITTED)
                    ("REQ-20261008-0006", user2_id, "NONE", "SUBMITTED"),

                    # REQ-0007 (APPROVED/ASSIGNED)
                    ("REQ-20261008-0007", user2_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0007", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),

                    # REQ-0008 (COMPLETED)
                    ("REQ-20261008-0008", user2_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0008", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),
                    ("REQ-20261008-0008", admin_id, "APPROVED/ASSIGNED", "IN_PROGRESS"),
                    ("REQ-20261008-0008", admin_id, "IN_PROGRESS", "COMPLETED"),

                    # REQ-0009 (CANCELLED)
                    ("REQ-20261008-0009", user2_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0009", user2_id, "SUBMITTED", "CANCELLED"),

                    # REQ-0010 (IN_PROGRESS)
                    ("REQ-20261008-0010", user2_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0010", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),
                    ("REQ-20261008-0010", admin_id, "APPROVED/ASSIGNED", "IN_PROGRESS"),

                    # REQ-0011 (COMPLETED)
                    ("REQ-20261008-0011", user2_id, "NONE", "SUBMITTED"),
                    ("REQ-20261008-0011", admin_id, "SUBMITTED", "APPROVED/ASSIGNED"),
                    ("REQ-20261008-0011", admin_id, "APPROVED/ASSIGNED", "IN_PROGRESS"),
                    ("REQ-20261008-0011", admin_id, "IN_PROGRESS", "COMPLETED")
                ]

                for ref, actor, old_st, new_st in histories:
                    cursor.execute(
                        """
                        INSERT INTO request_status_history (reference_id, actor_id, old_status, new_status, event_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """,
                        (ref, actor, old_st, new_st)
                    )

        print("Database seeded successfully with 12 presentation-ready demonstration requests and audit histories.")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database(include_sample_requests=True)
