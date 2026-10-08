class Resource:
    """
    Resource entity representing available certificate services/quotas.
    """
    def __init__(self, id=None, resource_id=None, service_name=None, capacity=0,
                 available_capacity=0, status="ACTIVE", owner_user_id=None, created_at=None):
        self.id = id
        self.resource_id = resource_id
        self.service_name = service_name
        self.capacity = capacity
        self.available_capacity = available_capacity
        self.status = status
        self.owner_user_id = owner_user_id
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            resource_id=row["resource_id"],
            service_name=row["service_name"],
            capacity=row["capacity"],
            available_capacity=row["available_capacity"],
            status=row["status"],
            owner_user_id=row["owner_user_id"],
            created_at=row["created_at"]
        )

    def is_available(self):
        return self.status == "ACTIVE" and self.available_capacity > 0
