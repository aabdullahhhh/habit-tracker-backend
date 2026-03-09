from datetime import datetime, timezone
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

    frequency_type = body.get("frequency_type", body.get("frequency", "daily")).lower()
    if frequency_type not in VALID_FREQUENCIES:
        return error(f"'frequency_type' must be one of: {', '.join(VALID_FREQUENCIES)}.", 400)

    habit = Habit(
        user_id=user_id,
        name=body["name"].strip(),
        description=body.get("description", "").strip(),
        frequency_type=frequency_type,
        category_id=body.get("category_id"),
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

    show_archived = request.args.get("archived", "false").lower() == "true"
    habits = (
        Habit.query
        .filter_by(user_id=user_id, is_archived=show_archived)
        .order_by(Habit.created_at.desc())
        .all()
    )
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

    if "frequency_type" in body:
        frequency_type = body["frequency_type"].lower()
        if frequency_type not in VALID_FREQUENCIES:
            return error(f"'frequency_type' must be one of: {', '.join(VALID_FREQUENCIES)}.", 400)
        habit.frequency_type = frequency_type

    if "category_id" in body:
        habit.category_id = body["category_id"]

    if "is_active" in body:
        if not isinstance(body["is_active"], bool):
            return error("'is_active' must be a boolean.", 400)
        habit.is_active = body["is_active"]

    habit.updated_at = datetime.now(timezone.utc)
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


# ── ARCHIVE ────────────────────────────────────────────────────────────────────
# PATCH /api/habits/<id>/archive
@habits_bp.route("/<int:habit_id>/archive", methods=["PATCH"])
def archive_habit(habit_id):
    user_id, err = require_auth()
    if err:
        return err

    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return error("Habit not found.", 404)

    if habit.is_archived:
        return error("Habit is already archived.", 400)

    habit.is_archived = True
    habit.archived_at = datetime.now(timezone.utc)
    db.session.commit()
    return success(habit.to_dict(), "Habit archived.")


# ── UNARCHIVE ──────────────────────────────────────────────────────────────────
# PATCH /api/habits/<id>/unarchive
@habits_bp.route("/<int:habit_id>/unarchive", methods=["PATCH"])
def unarchive_habit(habit_id):
    user_id, err = require_auth()
    if err:
        return err

    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return error("Habit not found.", 404)

    if not habit.is_archived:
        return error("Habit is not archived.", 400)

    habit.is_archived = False
    habit.archived_at = None
    db.session.commit()
    return success(habit.to_dict(), "Habit unarchived.")