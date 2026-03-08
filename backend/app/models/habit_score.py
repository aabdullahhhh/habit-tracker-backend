from app.models.db import db
from datetime import datetime


class HabitScore(db.Model):
    __tablename__ = "habit_scores"

    id             = db.Column(db.Integer, primary_key=True)
    habit_id       = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False, unique=True)

    # 0-100 score based on:
    # completion rate (last 30 days) × streak weight × frequency adherence
    # TODO (Phase 2): implement scoring.py to calculate this
    score          = db.Column(db.Float, nullable=False, default=0.0)

    calculated_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":            self.id,
            "habit_id":      self.habit_id,
            "score":         round(self.score, 1),
            "calculated_at": self.calculated_at.isoformat(),
        }
