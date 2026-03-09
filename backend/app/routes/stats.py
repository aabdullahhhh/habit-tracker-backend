from datetime import date, timedelta
from flask import Blueprint, session
from app.models.db import db
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.habit_score import HabitScore
from app.utils.responses import success, error
from app.utils.scoring import calculate_score

stats_bp = Blueprint("stats", __name__)

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_current_user_id():
    return session.get("user_id")


def get_habit_or_404(habit_id, user_id):
    return Habit.query.filter_by(id=habit_id, user_id=user_id).first()


def get_logs(habit_id):
    return HabitLog.query.filter_by(habit_id=habit_id).all()


# ── GET /api/habits/<id>/stats/30-day ─────────────────────────────────────────
# 30-day completion graph — one entry per day for the last 30 days
@stats_bp.route("/<int:habit_id>/stats/30-day", methods=["GET"])
def thirty_day_graph(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    logs = get_logs(habit_id)
    completed_set = {log.completed_date for log in logs}

    today = date.today()
    graph = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        graph.append({
            "date": day.isoformat(),
            "completed": day in completed_set,
        })

    return success("30-day graph retrieved", {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "days": graph,
        "total_completions": len([d for d in graph if d["completed"]]),
        "completion_rate": round(
            len([d for d in graph if d["completed"]]) / 30 * 100, 1
        ),
    })


# ── GET /api/habits/<id>/stats/heatmap ────────────────────────────────────────
# 365-day heatmap — date + completed boolean for the last year
@stats_bp.route("/<int:habit_id>/stats/heatmap", methods=["GET"])
def heatmap(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    logs = get_logs(habit_id)
    completed_set = {log.completed_date for log in logs}

    today = date.today()
    days = []
    for i in range(364, -1, -1):
        day = today - timedelta(days=i)
        days.append({
            "date": day.isoformat(),
            "completed": day in completed_set,
        })

    total = len([d for d in days if d["completed"]])

    return success("Heatmap retrieved", {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "days": days,
        "total_completions": total,
        "completion_rate": round(total / 365 * 100, 1),
    })


# ── GET /api/habits/<id>/stats/best-day ───────────────────────────────────────
# Best day of week — which day has the most check-ins
@stats_bp.route("/<int:habit_id>/stats/best-day", methods=["GET"])
def best_day(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    logs = get_logs(habit_id)

    # Count completions per day of week (0=Monday, 6=Sunday)
    day_counts = {i: 0 for i in range(7)}
    for log in logs:
        dow = log.completed_date.weekday()
        day_counts[dow] += 1

    total = sum(day_counts.values())

    breakdown = [
        {
            "day": DAYS_OF_WEEK[i],
            "completions": day_counts[i],
            "percentage": round(day_counts[i] / total * 100, 1) if total > 0 else 0,
        }
        for i in range(7)
    ]

    best = max(breakdown, key=lambda x: x["completions"])
    worst = min(breakdown, key=lambda x: x["completions"])

    return success("Best day retrieved", {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "best_day": best["day"],
        "worst_day": worst["day"],
        "breakdown": breakdown,
        "total_completions": total,
    })


# ── GET /api/habits/<id>/stats/mood-trend ─────────────────────────────────────
# Mood trend — mood over the last 30 days
@stats_bp.route("/<int:habit_id>/stats/mood-trend", methods=["GET"])
def mood_trend(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    logs = get_logs(habit_id)

    today = date.today()
    last_30_start = today - timedelta(days=29)

    # Only logs with mood in last 30 days
    mood_logs = [
        log for log in logs
        if log.mood is not None and log.completed_date >= last_30_start
    ]
    mood_logs.sort(key=lambda l: l.completed_date)

    trend = [
        {
            "date": log.completed_date.isoformat(),
            "mood": log.mood,
        }
        for log in mood_logs
    ]

    avg_mood = (
        round(sum(e["mood"] for e in trend) / len(trend), 2)
        if trend else None
    )

    # Simple trend direction — compare first half avg vs second half avg
    trend_direction = None
    if len(trend) >= 4:
        mid = len(trend) // 2
        first_half_avg = sum(e["mood"] for e in trend[:mid]) / mid
        second_half_avg = sum(e["mood"] for e in trend[mid:]) / (len(trend) - mid)
        if second_half_avg > first_half_avg + 0.3:
            trend_direction = "improving"
        elif second_half_avg < first_half_avg - 0.3:
            trend_direction = "declining"
        else:
            trend_direction = "stable"

    return success("Mood trend retrieved", {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "mood_trend": trend,
        "average_mood": avg_mood,
        "trend_direction": trend_direction,
        "total_mood_entries": len(trend),
    })


# ── GET /api/habits/<id>/stats/score ──────────────────────────────────────────
# Current habit score (0-100)
@stats_bp.route("/<int:habit_id>/stats/score", methods=["GET"])
def habit_score(habit_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    habit = get_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit not found", 404)

    logs = get_logs(habit_id)
    completed_dates = [log.completed_date for log in logs]
    mood_map = {
        log.completed_date: log.mood
        for log in logs
        if log.mood is not None
    }

    # Calculate live score
    score = calculate_score(completed_dates, mood_map)

    # Also return last saved score from DB if exists
    saved = HabitScore.query.filter_by(habit_id=habit_id).first()

    return success("Score retrieved", {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "score": score,
        "last_saved_score": saved.score if saved else None,
        "last_calculated_at": saved.calculated_at.isoformat() if saved else None,
    })
