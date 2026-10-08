import datetime
import uuid
from database.db import get_db_connection
from services.validation_service import ValidationService, ValidationError
from models.service_request import ServiceRequest
from models.resource import Resource
from models.status_history import RequestStatusHistory

class RequestService:
    """
    Manages request creation, atomic submission, state transitions,
    resource allocation/release, and audit history.
    """

    @staticmethod
    def generate_reference_id(conn):
        """
        Generates a unique request reference ID.
        Format: REQ-YYYYMMDD-XXXX
        Guaranteed to be unique.
        """
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM service_requests WHERE reference_id LIKE ?", (f"REQ-{today_str}-%",))
        count = cursor.fetchone()["total"] + 1
        
        while True:
            candidate_id = f"REQ-{today_str}-{count:04d}"
            cursor.execute("SELECT id FROM service_requests WHERE reference_id = ?", (candidate_id,))
            if not cursor.fetchone():
                return candidate_id
            count += 1

    @classmethod
    def submit_request(cls, user_id, service_id, requester_name, phone,
                       description, reference_details, chargeable_amount,
                       db_path=None):
        """
        Atomically validates, computes charges, snapshots master data,
        reserves resource capacity, records history, and creates the request.
        BR6: Atomic rollback on any failure.
        BR7: All-or-nothing submission transaction.
        """
        conn = get_db_connection(db_path)
        try:
            # Step 1: Input details validation
            ValidationService.validate_details(
                requester_name=requester_name,
                phone=phone,
                description=description,
                reference_details=reference_details
            )

            # Step 2-6: Recheck all eligibility immediately before acceptance inside transaction
            user_row, service_row = ValidationService.validate_eligibility(user_id, service_id, conn)

            # Step 7: Calculate charge
            charge = ValidationService.calculate_charge(chargeable_amount)

            # Generate unique reference ID
            reference_id = cls.generate_reference_id(conn)

            # Master data snapshot (BR3)
            service_name_snapshot = service_row["service_name"]
            service_value_snapshot = float(service_row["capacity"])

            # Step 8: Database Transaction
            with conn:
                # Double-check capacity and lock row in SQLite
                cur = conn.cursor()
                cur.execute(
                    "SELECT available_capacity, status FROM resources WHERE resource_id = ?",
                    (service_id,)
                )
                res_check = cur.fetchone()
                if not res_check or res_check["status"] != "ACTIVE" or res_check["available_capacity"] <= 0:
                    raise ValidationError("The selected service/resource is currently unavailable.")

                # Decrement available capacity (reserve resource)
                cur.execute(
                    """
                    UPDATE resources
                    SET available_capacity = available_capacity - 1
                    WHERE resource_id = ? AND available_capacity > 0
                    """,
                    (service_id,)
                )
                if cur.rowcount == 0:
                    raise ValidationError("Failed to reserve service capacity.")

                # Insert service request
                cur.execute(
                    """
                    INSERT INTO service_requests (
                        reference_id, user_id, service_id, service_name_snapshot,
                        service_value_snapshot, requester_name, phone, description,
                        reference_details, charge, status, resource_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUBMITTED', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (
                        reference_id, user_id, service_id, service_name_snapshot,
                        service_value_snapshot, requester_name.strip(), str(phone).strip(),
                        description.strip(), reference_details.strip(), charge, service_id
                    )
                )

                # Insert status history entry
                cur.execute(
                    """
                    INSERT INTO request_status_history (
                        reference_id, actor_id, old_status, new_status, event_at
                    ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (reference_id, user_id, "NONE", "SUBMITTED")
                )

            # Return newly created request record
            return cls.get_request_by_reference(reference_id, conn)

        finally:
            conn.close()

    @staticmethod
    def get_request_by_reference(reference_id, conn=None, close_after=False):
        """
        Retrieves a single service request with its details.
        """
        should_close = False
        if conn is None:
            conn = get_db_connection()
            should_close = True

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM service_requests WHERE reference_id = ?", (reference_id,))
            row = cursor.fetchone()
            return ServiceRequest.from_row(row) if row else None
        finally:
            if should_close:
                conn.close()

    @staticmethod
    def get_user_requests(user_id, conn=None):
        """
        Retrieves all requests for a specific user (BR10).
        """
        should_close = False
        if conn is None:
            conn = get_db_connection()
            should_close = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM service_requests
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,)
            )
            rows = cursor.fetchall()
            return [ServiceRequest.from_row(r) for r in rows]
        finally:
            if should_close:
                conn.close()

    @staticmethod
    def get_all_requests(conn=None):
        """
        Retrieves all requests across all users for administrator dashboard.
        """
        should_close = False
        if conn is None:
            conn = get_db_connection()
            should_close = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT sr.*, u.username, u.name as user_full_name
                FROM service_requests sr
                JOIN users u ON sr.user_id = u.id
                ORDER BY sr.id DESC
                """
            )
            rows = cursor.fetchall()
            return rows
        finally:
            if should_close:
                conn.close()

    @staticmethod
    def get_request_history(reference_id, conn=None):
        """
        Retrieves the audit trail of status transitions for a request.
        """
        should_close = False
        if conn is None:
            conn = get_db_connection()
            should_close = True

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT h.*, u.username as actor_username, u.role as actor_role
                FROM request_status_history h
                LEFT JOIN users u ON h.actor_id = u.id
                WHERE h.reference_id = ?
                ORDER BY h.id ASC
                """,
                (reference_id,)
            )
            rows = cursor.fetchall()
            return rows
        finally:
            if should_close:
                conn.close()

    @classmethod
    def cancel_request(cls, reference_id, user_id, db_path=None):
        """
        BR9 - Cancellation logic:
        - User can cancel only their own SUBMITTED request.
        - Changes status to CANCELLED.
        - Releases reserved resource capacity exactly ONCE.
        - Repeated cancellation has no effect and shows clear error.
        - If unauthorized or invalid status, rejects without partial changes.
        """
        conn = get_db_connection(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM service_requests WHERE reference_id = ?", (reference_id,))
            req = cursor.fetchone()
            if not req:
                raise ValidationError("Request not found.")

            # BR10: Ownership check
            if req["user_id"] != user_id:
                raise ValidationError("Access denied.")

            # Check status
            if req["status"] == "CANCELLED":
                raise ValidationError("Request has already been cancelled.")

            if req["status"] != "SUBMITTED":
                raise ValidationError("Only SUBMITTED requests can be cancelled.")

            # Perform atomic cancellation transaction
            with conn:
                cur = conn.cursor()
                # 1. Update request status to CANCELLED
                cur.execute(
                    """
                    UPDATE service_requests
                    SET status = 'CANCELLED', updated_at = CURRENT_TIMESTAMP, cancelled_at = CURRENT_TIMESTAMP
                    WHERE reference_id = ? AND status = 'SUBMITTED'
                    """,
                    (reference_id,)
                )
                if cur.rowcount == 0:
                    raise ValidationError("Request has already been cancelled.")

                # 2. Release reserved resource capacity exactly ONCE
                cur.execute(
                    """
                    UPDATE resources
                    SET available_capacity = available_capacity + 1
                    WHERE resource_id = ?
                    """,
                    (req["resource_id"],)
                )

                # 3. Create status history
                cur.execute(
                    """
                    INSERT INTO request_status_history (
                        reference_id, actor_id, old_status, new_status, event_at
                    ) VALUES (?, ?, 'SUBMITTED', 'CANCELLED', CURRENT_TIMESTAMP)
                    """,
                    (reference_id, user_id)
                )

            return True
        finally:
            conn.close()

    @classmethod
    def advance_status(cls, reference_id, next_status, admin_user, db_path=None):
        """
        BR8 & BR10 - Administrator moves request through strictly valid stages:
        SUBMITTED -> APPROVED/ASSIGNED -> IN_PROGRESS -> COMPLETED
        Skipping stages is strictly forbidden.
        """
        if not admin_user or admin_user.role != "ADMINISTRATOR":
            raise ValidationError("Access denied.")

        conn = get_db_connection(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM service_requests WHERE reference_id = ?", (reference_id,))
            req = cursor.fetchone()
            if not req:
                raise ValidationError("Request not found.")

            current_status = req["status"]
            # Validate transition using BR8 map
            ValidationService.validate_status_transition(current_status, next_status)

            # Perform transition transaction
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE service_requests
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE reference_id = ? AND status = ?
                    """,
                    (next_status, reference_id, current_status)
                )
                if cur.rowcount == 0:
                    raise ValidationError("Concurrent status modification detected.")

                cur.execute(
                    """
                    INSERT INTO request_status_history (
                        reference_id, actor_id, old_status, new_status, event_at
                    ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (reference_id, admin_user.id, current_status, next_status)
                )

            return True
        finally:
            conn.close()

    @staticmethod
    def get_resource(resource_id, conn=None):
        """
        Gets a single resource by its ID.
        """
        should_close = False
        if conn is None:
            conn = get_db_connection()
            should_close = True

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resources WHERE resource_id = ?", (resource_id,))
            row = cursor.fetchone()
            return Resource.from_row(row) if row else None
        finally:
            if should_close:
                conn.close()

    @staticmethod
    def get_all_resources(conn=None):
        """
        Retrieves all resources for request selection and administration.
        """
        should_close = False
        if conn is None:
            conn = get_db_connection()
            should_close = True

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resources ORDER BY resource_id ASC")
            rows = cursor.fetchall()
            return [Resource.from_row(r) for r in rows]
        finally:
            if should_close:
                conn.close()
