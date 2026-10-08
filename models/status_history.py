class RequestStatusHistory:
    """
    Audit history entity tracking all status changes on a request.
    """
    def __init__(self, id=None, reference_id=None, actor_id=None, old_status=None, new_status=None, event_at=None):
        self.id = id
        self.reference_id = reference_id
        self.actor_id = actor_id
        self.old_status = old_status
        self.new_status = new_status
        self.event_at = event_at

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            reference_id=row["reference_id"],
            actor_id=row["actor_id"],
            old_status=row["old_status"],
            new_status=row["new_status"],
            event_at=row["event_at"]
        )
