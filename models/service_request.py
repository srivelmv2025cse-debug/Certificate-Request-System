class ServiceRequest:
    """
    ServiceRequest entity representing a submitted certificate request.
    """
    def __init__(self, id=None, reference_id=None, user_id=None, service_id=None,
                 service_name_snapshot=None, service_value_snapshot=0.0,
                 requester_name=None, phone=None, description=None,
                 reference_details=None, charge=0.0, status="SUBMITTED",
                 resource_id=None, created_at=None, updated_at=None, cancelled_at=None):
        self.id = id
        self.reference_id = reference_id
        self.user_id = user_id
        self.service_id = service_id
        self.service_name_snapshot = service_name_snapshot
        self.service_value_snapshot = service_value_snapshot
        self.requester_name = requester_name
        self.phone = phone
        self.description = description
        self.reference_details = reference_details
        self.charge = charge
        self.status = status
        self.resource_id = resource_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.cancelled_at = cancelled_at

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            reference_id=row["reference_id"],
            user_id=row["user_id"],
            service_id=row["service_id"],
            service_name_snapshot=row["service_name_snapshot"],
            service_value_snapshot=row["service_value_snapshot"],
            requester_name=row["requester_name"],
            phone=row["phone"],
            description=row["description"],
            reference_details=row["reference_details"],
            charge=row["charge"],
            status=row["status"],
            resource_id=row["resource_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            cancelled_at=row["cancelled_at"] if "cancelled_at" in row.keys() else None
        )
