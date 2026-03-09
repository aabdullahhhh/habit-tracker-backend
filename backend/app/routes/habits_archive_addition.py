# ── Add these two routes to the bottom of routes/habits.py ──────────────────
# Make sure to import datetime at the top of habits.py:
#   from datetime import datetime, timezone

from datetime import datetime, timezone

# PATCH /api/habits/<id>/archive
@habits_bp.route("/<int:habit_id>/archive", methods=["PATCH"])
def archive_habit(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return error("Habit not found", 404)

    if habit.is_archived:
        return error("Habit is already archived", 400)

    habit.is_archived = True
    habit.archived_at = datetime.now(timezone.utc)
    db.session.commit()
    return success("Habit archived", habit.to_dict())


# PATCH /api/habits/<id>/unarchive
@habits_bp.route("/<int:habit_id>/unarchive", methods=["PATCH"])
def unarchive_habit(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return error("Habit not found", 404)

    if not habit.is_archived:
        return error("Habit is not archived", 400)

    habit.is_archived = False
    habit.archived_at = None
    db.session.commit()
    return success("Habit unarchived", habit.to_dict())
