from app.models.db import db
from datetime import datetime, date


class HabitLog(db.Model):
    __tablename__ = "habit_logs"

    id             = db.Column(db.Integer, primary_key=True)
    habit_id       = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)

    completed_date = db.Column(db.Date, nullable=False, default=date.today)
    mood           = db.Column(db.Integer, nullable=True)
    note           = db.Column(db.Text, nullable=True)

    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("habit_id", "completed_date", name="uq_habit_log_per_day"),
    )

    def to_dict(self):
        return {
            "id":             self.id,
            "habit_id":       self.habit_id,
            "completed_date": self.completed_date.isoformat(),
            "mood":           self.mood,
            "note":           self.note,
            "created_at":     self.created_at.isoformat(),
        }