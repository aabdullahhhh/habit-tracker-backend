from app.models.db import db
from datetime import datetime
import json
VALID_FREQUENCIES = ["daily", "weekly", "custom"]

class Habit(db.Model):
    __tablename__ = "habits"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # --- Phase 1 addition: category (optional) ---
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # --- Phase 1 addition: frequency overhaul ---
    # frequency_type: "daily" | "weekly" | "custom"
    # frequency_days: JSON list of weekday ints — [0,2,4] = Mon/Wed/Fri
    #   only used when frequency_type = "custom"
    #   0 = Monday, 1 = Tuesday, ..., 6 = Sunday
    frequency_type = db.Column(db.String(20), nullable=False, default="daily")
    frequency_days = db.Column(db.Text, nullable=True)  # stored as JSON string

    is_active   = db.Column(db.Boolean, default=True)

    # --- Phase 1 addition: soft archive ---
    is_archived    = db.Column(db.Boolean, default=False)
    archived_at    = db.Column(db.DateTime, nullable=True)

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relationships ---
    logs  = db.relationship("HabitLog", backref="habit", lazy=True, cascade="all, delete-orphan")
    score = db.relationship("HabitScore", backref="habit", uselist=False, cascade="all, delete-orphan")

    # TODO (Phase 7): Add challenge entries relationship

    # --- Helpers ---
    def get_frequency_days(self):
        """Returns frequency_days as a Python list. e.g. [0, 2, 4]"""
        if self.frequency_days:
            return json.loads(self.frequency_days)
        return []

    def set_frequency_days(self, days: list):
        """Accepts a list of ints and stores as JSON string."""
        self.frequency_days = json.dumps(days)

    def to_dict(self):
        return {
            "id":              self.id,
            "user_id":         self.user_id,
            "category_id":     self.category_id,
            "name":            self.name,
            "description":     self.description,
            "frequency_type":  self.frequency_type,
            "frequency_days":  self.get_frequency_days(),
            "is_active":       self.is_active,
            "is_archived":     self.is_archived,
            "archived_at":     self.archived_at.isoformat() if self.archived_at else None,
            "created_at":      self.created_at.isoformat(),
            "updated_at":      self.updated_at.isoformat(),
        }
