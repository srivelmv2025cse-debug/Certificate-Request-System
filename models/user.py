class User:
    """
    User entity representing system actors (USER or ADMINISTRATOR).
    """
    def __init__(self, id=None, name=None, username=None, password=None, role=None, status="ACTIVE", created_at=None):
        self.id = id
        self.name = name
        self.username = username
        self.password = password
        self.role = role
        self.status = status
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            username=row["username"],
            password=row["password"],
            role=row["role"],
            status=row["status"],
            created_at=row["created_at"]
        )

    def is_active(self):
        return self.status == "ACTIVE"

    def is_admin(self):
        return self.role == "ADMINISTRATOR"
