from app.models.db import db
from datetime import datetime

# TODO (Phase 7): Implement full challenge logic
# This is a skeleton — do not use until Phase 7


class Challenge(db.Model):
    __tablename__ = "challenges"

    id               = db.Column(db.Integer, primary_key=True)
    creator_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title            = db.Column(db.String(120), nullable=False)
    description      = db.Column(db.Text, nullable=True)

    # The habit template users will follow during the challenge
    habit_template   = db.Column(db.String(120), nullable=False)

    duration_days    = db.Column(db.Integer, nullable=False, default=30)
    start_date       = db.Column(db.Date, nullable=True)
    end_date         = db.Column(db.Date, nullable=True)

    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    entries = db.relationship("ChallengeEntry", backref="challenge", lazy=True, cascade="all, delete-orphan")

    # TODO (Phase 7): Add leaderboard query helper

    def to_dict(self):
        return {
            "id":             self.id,
            "creator_id":     self.creator_id,
            "title":          self.title,
            "description":    self.description,
            "habit_template": self.habit_template,
            "duration_days":  self.duration_days,
            "start_date":     self.start_date.isoformat() if self.start_date else None,
            "end_date":       self.end_date.isoformat() if self.end_date else None,
            "created_at":     self.created_at.isoformat(),
        }
