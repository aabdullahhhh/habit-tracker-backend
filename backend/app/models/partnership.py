from app.models.db import db
from datetime import datetime

# TODO (Phase 7): Implement full partnership logic
# This is a skeleton — do not use until Phase 7


class Partnership(db.Model):
    __tablename__ = "partnerships"

    id            = db.Column(db.Integer, primary_key=True)
    requester_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    addressee_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # status: "pending" | "active" | "rejected"
    status        = db.Column(db.String(20), nullable=False, default="pending")

    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # TODO (Phase 7): Add shared habits visibility logic
    # TODO (Phase 7): Add to_dict()

    def to_dict(self):
        return {
            "id":           self.id,
            "requester_id": self.requester_id,
            "addressee_id": self.addressee_id,
            "status":       self.status,
            "created_at":   self.created_at.isoformat(),
        }
