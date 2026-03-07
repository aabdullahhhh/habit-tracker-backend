from datetime import datetime
from flask import Blueprint, request, session

from ..models.db import db
from ..models.habit import Habit, VALID_FREQUENCIES
from ..utils.responses import success, error, validate_required

habits_bp = Blueprint("habits", __name__)


def get_current_user_id():
    """Return the logged-in user's id or None."""
    return session.get("user_id")


def require_auth():
    """Return (user_id, None) or (None, error_response)."""
    uid = get_current_user_id()
    if not uid:
        return None, error("Authentication required.", 401)
    return uid, None


# ── CREATE ─────────────────────────────────────────────────────────────────────
# POST /api/habits/
@habits_bp.route("/", methods=["POST"])
def create_habit():
    user_id, err = require_auth()
    if err:
        return err

    body = request.get_json(silent=True) or {}

    missing = validate_required(body, ["name"])
    if missing:
        return error("Habit 'name' is required.", 400)

    frequency = body.get("frequency", "daily").lower()
    if frequency not in VALID_FREQUENCIES:
        return error(f"'frequency' must be one of: {', '.join(VALID_FREQUENCIES)}.", 400)

    habit = Habit(
        user_id=user_id,
        name=body["name"].strip(),
        description=body.get("description", "").strip(),
        frequency=frequency,
    )
    db.session.add(habit)
    db.session.commit()

    return success(habit.to_dict(), "Habit created.", 201)


# ── READ ALL ───────────────────────────────────────────────────────────────────
# GET /api/habits/
@habits_bp.route("/", methods=["GET"])
def list_habits():
    user_id, err = require_auth()
    if err:
        return err

    habits = Habit.query.filter_by(user_id=user_id).order_by(Habit.created_at.desc()).all()
    return success([h.to_dict() for h in habits])


# ── READ ONE ───────────────────────────────────────────────────────────────────
# GET /api/habits/<id>
@habits_bp.route("/<int:habit_id>", methods=["GET"])
def get_habit(habit_id):
    user_id, err = require_auth()
    if err:
        return err

    habit = db.session.get(Habit, habit_id)
    if not habit or habit.user_id != user_id:
        return error("Habit not found.", 404)

    return success(habit.to_dict())


# ── UPDATE ─────────────────────────────────────────────────────────────────────
# PATCH /api/habits/<id>
@habits_bp.route("/<int:habit_id>", methods=["PATCH"])
def update_habit(habit_id):
    user_id, err = require_auth()
    if err:
        return err

    habit = db.session.get(Habit, habit_id)
    if not habit or habit.user_id != user_id:
        return error("Habit not found.", 404)

    body = request.get_json(silent=True) or {}

    if "name" in body:
        name = body["name"].strip()
        if not name:
            return error("'name' cannot be empty.", 400)
        habit.name = name

    if "description" in body:
        habit.description = body["description"].strip()

    if "frequency" in body:
        frequency = body["frequency"].lower()
        if frequency not in VALID_FREQUENCIES:
            return error(f"'frequency' must be one of: {', '.join(VALID_FREQUENCIES)}.", 400)
        habit.frequency = frequency

    if "is_active" in body:
        if not isinstance(body["is_active"], bool):
            return error("'is_active' must be a boolean.", 400)
        habit.is_active = body["is_active"]

    habit.updated_at = datetime.utcnow()
    db.session.commit()

    return success(habit.to_dict(), "Habit updated.")


# ── DELETE ─────────────────────────────────────────────────────────────────────
# DELETE /api/habits/<id>
@habits_bp.route("/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    user_id, err = require_auth()
    if err:
        return err

    habit = db.session.get(Habit, habit_id)
    if not habit or habit.user_id != user_id:
        return error("Habit not found.", 404)

    db.session.delete(habit)
    db.session.commit()

    return success(message="Habit deleted.")
