from datetime import date
from flask import Blueprint, request, session
from app.models.db import db
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.utils.responses import success, error
from app.utils.streak import calculate_streaks

logs_bp = Blueprint("logs", __name__)


def get_current_user_id():
    return session.get("user_id")


def get_habit_or_404(habit_id, user_id):
    """Return habit if it belongs to user, otherwise None (no leaking ownership)."""
    return Habit.query.filter_by(id=habit_id, user_id=user_id).first()


def get_all_dates(habit_id: int) -> list[date]:
    logs = HabitLog.query.filter_by(habit_id=habit_id).all()
    return [log.completed_date for log in logs]


# POST /api/habits/<id>/logs — check in today
@logs_bp.route("/", methods=["POST"])
def check_in(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    data = request.get_json() or {}
    today = date.today()

    # Validate mood
    mood = data.get("mood")
    if mood is not None:
        if not isinstance(mood, int) or mood < 1 or mood > 5:
            return error("Mood must be an integer between 1 and 5", 400)

    note = (data.get("note") or "").strip() or None

    # Block duplicate check-ins
    existing = HabitLog.query.filter_by(
        habit_id=habit_id, completed_date=today
    ).first()
    if existing:
        return error("Already checked in today", 409)

    log = HabitLog(
        habit_id=habit_id,
        completed_date=today,
        mood=mood,
        note=note,
    )
    db.session.add(log)
    db.session.commit()

    # Streak info
    all_dates = get_all_dates(habit_id)
    streaks = calculate_streaks(all_dates)

    return success(
        "Checked in successfully",
        {
            "log": log.to_dict(),
            "current_streak": streaks["current_streak"],
            "longest_streak": streaks["longest_streak"],
            "total_completions": streaks["total_completions"],
        },
        201,
    )


# DELETE /api/habits/<id>/logs — undo today's check-in
@logs_bp.route("/", methods=["DELETE"])
def undo_check_in(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    today = date.today()
    log = HabitLog.query.filter_by(
        habit_id=habit_id, completed_date=today
    ).first()

    if not log:
        return error("No check-in found for today", 404)

    db.session.delete(log)
    db.session.commit()
    return success("Check-in removed")


# GET /api/habits/<id>/logs — full history + streaks
@logs_bp.route("/", methods=["GET"])
def get_logs(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    logs = (
        HabitLog.query.filter_by(habit_id=habit_id)
        .order_by(HabitLog.completed_date.desc())
        .all()
    )

    all_dates = [log.completed_date for log in logs]
    streaks = calculate_streaks(all_dates)

    return success(
        "Logs retrieved",
        {
            "logs": [log.to_dict() for log in logs],
            "current_streak": streaks["current_streak"],
            "longest_streak": streaks["longest_streak"],
            "total_completions": streaks["total_completions"],
        },
    )
