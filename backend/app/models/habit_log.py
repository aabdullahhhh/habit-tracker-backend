from app.models.db import db
from datetime import datetime, date


class HabitLog(db.Model):
    __tablename__ = "habit_logs"

    id             = db.Column(db.Integer, primary_key=True)
    habit_id       = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # DATE only (not DateTime) — timezone-safe, one entry per day per habit
    # DECISION: Using DATE not DATETIME so a check-in at 11pm in Karachi
    # doesn't bleed into the next UTC day and break streak logic.
    completed_date = db.Column(db.Date, nullable=False, default=date.today)

    # Mood rating: 1 (terrible) → 5 (great). Optional.
    mood           = db.Column(db.Integer, nullable=True)

    # Optional journal note on check-in
    note           = db.Column(db.Text, nullable=True)

    # TODO (Phase 3): ai_companion_message = db.Column(db.Text, nullable=True)
    # Store the AI check-in companion response so we don't re-call Groq on refresh

    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Constraints ---
    # A habit can only be completed once per day
    __table_args__ = (
        db.UniqueConstraint("habit_id", "completed_date", name="uq_habit_log_per_day"),
    )

    def to_dict(self):
        return {
            "id":             self.id,
            "habit_id":       self.habit_id,
            "user_id":        self.user_id,
            "completed_date": self.completed_date.isoformat(),
            "mood":           self.mood,
            "note":           self.note,
            "created_at":     self.created_at.isoformat(),
        }
