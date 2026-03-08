from app.models.db import db
from datetime import datetime

# TODO (Phase 7): Implement full challenge entry logic
# This is a skeleton — do not use until Phase 7


class ChallengeEntry(db.Model):
    __tablename__ = "challenge_entries"

    id           = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    joined_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # TODO (Phase 7): Add completion_rate computed from HabitLogs during challenge period
    # TODO (Phase 7): Add leaderboard ranking logic

    __table_args__ = (
        db.UniqueConstraint("challenge_id", "user_id", name="uq_challenge_entry"),
    )

    def to_dict(self):
        return {
            "id":           self.id,
            "challenge_id": self.challenge_id,
            "user_id":      self.user_id,
            "joined_at":    self.joined_at.isoformat(),
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
