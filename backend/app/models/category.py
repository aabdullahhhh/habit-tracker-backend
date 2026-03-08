from app.models.db import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = "categories"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name       = db.Column(db.String(50), nullable=False)
    color      = db.Column(db.String(7), nullable=False, default="#6366f1")  # hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    habits = db.relationship("Habit", backref="category", lazy=True)

    def to_dict(self):
        return {
            "id":         self.id,
            "user_id":    self.user_id,
            "name":       self.name,
            "color":      self.color,
            "created_at": self.created_at.isoformat(),
        }
