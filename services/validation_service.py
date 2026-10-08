import re
from config import Config

class ValidationError(Exception):
    """Custom exception raised for business rule and validation failures."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ValidationService:
    """
    Validates business rules, user eligibility, input details, and status transitions.
    """

    STATUS_TRANSITION_MAP = {
        "SUBMITTED": ["APPROVED/ASSIGNED"],
        "APPROVED/ASSIGNED": ["IN_PROGRESS"],
        "IN_PROGRESS": ["COMPLETED"],
        "COMPLETED": [],
        "CANCELLED": []
    }

    @staticmethod
    def validate_user(user):
        """
        Validates user status (BR2: User must be ACTIVE).
        """
        if not user:
            raise ValidationError("User not found.")
        status = user["status"] if isinstance(user, dict) or hasattr(user, "__getitem__") else user.status
        if status != "ACTIVE":
            raise ValidationError("User is inactive.")
        return True

    @staticmethod
    def validate_service(service_resource):
        """
        Validates resource status and available capacity (BR2).
        """
        if not service_resource:
            raise ValidationError("Selected service does not exist.")
        
        status = service_resource["status"] if hasattr(service_resource, "__getitem__") else service_resource.status
        if status != "ACTIVE":
            raise ValidationError("The selected service is inactive.")
            
        avail = service_resource["available_capacity"] if hasattr(service_resource, "__getitem__") else service_resource.available_capacity
        if avail <= 0:
            raise ValidationError("The selected service/resource is currently unavailable.")
        return True

    @staticmethod
    def validate_details(requester_name, phone, description, reference_details):
        """
        BR5 - Details validation.
        - Name cannot be blank.
        - Phone must be exactly 10 digits.
        - Description and reference details must be present and non-empty.
        """
        if not requester_name or not str(requester_name).strip():
            raise ValidationError("Name cannot be blank.")
            
        phone_str = str(phone).strip() if phone is not None else ""
        if not re.fullmatch(r"\d{10}", phone_str):
            raise ValidationError("Phone number must contain exactly 10 digits.")
            
        if not description or not str(description).strip():
            raise ValidationError("Description cannot be blank.")
            
        if not reference_details or not str(reference_details).strip():
            raise ValidationError("Reference details cannot be blank.")
            
        return True

    @staticmethod
    def check_active_request_limit(user_id, conn):
        """
        BR1 - Active request limit.
        User can have at most 5 active requests (not COMPLETED and not CANCELLED).
        A 6th active request must be rejected.
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) AS active_count
            FROM service_requests
            WHERE user_id = ? AND status NOT IN ('COMPLETED', 'CANCELLED')
            """,
            (user_id,)
        )
        row = cursor.fetchone()
        active_count = row["active_count"] if row else 0
        if active_count >= Config.MAX_ACTIVE_REQUESTS:
            raise ValidationError("Active request limit exceeded. A user can have at most 5 active requests.")
        return active_count

    @staticmethod
    def calculate_charge(amount):
        """
        BR4 - EXACT charge logic:
        If chargeable amount is below Rs.1000: charge = Rs.50
        If amount is Rs.1000 or above: charge = Rs.0
        If the scenario is not chargeable: charge = Rs.0
        Boundary values:
        999  -> 50.0
        1000 -> 0.0
        1001 -> 0.0
        """
        if amount is None:
            return 0.0
        try:
            amt = float(amount)
        except (ValueError, TypeError):
            raise ValidationError("Invalid chargeable amount format.")

        if amt < 0:
            return 0.0
        if amt < Config.CHARGE_THRESHOLD:
            return Config.BELOW_THRESHOLD_CHARGE
        else:
            return Config.ABOVE_THRESHOLD_CHARGE

    @classmethod
    def validate_eligibility(cls, user_id, service_id, conn):
        """
        BR2 - Comprehensive eligibility recheck before acceptance:
        1. User is ACTIVE
        2. Service is ACTIVE
        3. User within active request limit
        4. Requested resource has available capacity > 0
        """
        cursor = conn.cursor()
        # 1. User check
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        cls.validate_user(user_row)

        # 2 & 4. Service check
        cursor.execute("SELECT * FROM resources WHERE resource_id = ?", (service_id,))
        service_row = cursor.fetchone()
        cls.validate_service(service_row)

        # 3. Active request limit check
        cls.check_active_request_limit(user_id, conn)

        return user_row, service_row

    @classmethod
    def validate_status_transition(cls, current_status, next_status):
        """
        BR8 - Status flow validation:
        SUBMITTED -> APPROVED/ASSIGNED -> IN_PROGRESS -> COMPLETED
        Skipping stages or invalid transitions must be rejected.
        """
        allowed_next = cls.STATUS_TRANSITION_MAP.get(current_status, [])
        if next_status not in allowed_next:
            raise ValidationError(
                f"Invalid status transition from '{current_status}' to '{next_status}'. "
                f"Allowed transition: {allowed_next if allowed_next else 'None (Terminal state)'}"
            )
        return True
