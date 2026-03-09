from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)


def recalculate_all_scores(app):
    """
    Recalculate scores for every non-archived habit.
    Runs nightly at midnight.
    """
    with app.app_context():
        from app.models.db import db
        from app.models.habit import Habit
        from app.models.habit_log import HabitLog
        from app.models.habit_score import HabitScore
        from app.utils.scoring import calculate_score
        from datetime import datetime, timezone

        habits = Habit.query.filter_by(is_archived=False).all()
        updated = 0

        for habit in habits:
            logs = HabitLog.query.filter_by(habit_id=habit.id).all()
            completed_dates = [log.completed_date for log in logs]
            mood_map = {
                log.completed_date: log.mood
                for log in logs
                if log.mood is not None
            }

            score = calculate_score(completed_dates, mood_map)

            # Upsert — update existing score or create new one
            habit_score = HabitScore.query.filter_by(habit_id=habit.id).first()
            if habit_score:
                habit_score.score = score
                habit_score.calculated_at = datetime.now(timezone.utc)
            else:
                habit_score = HabitScore(
                    habit_id=habit.id,
                    score=score,
                    calculated_at=datetime.now(timezone.utc),
                )
                db.session.add(habit_score)

            updated += 1

        db.session.commit()
        logger.info(f"[Scheduler] Recalculated scores for {updated} habits.")


def detect_slipping_habits(app):
    """
    Detect habits that haven't been checked in for 2+ days.
    Logs them for now — Phase 6 will send email alerts.
    """
    with app.app_context():
        from app.models.habit import Habit
        from app.models.habit_log import HabitLog
        from datetime import date, timedelta

        today = date.today()
        two_days_ago = today - timedelta(days=2)

        habits = Habit.query.filter_by(is_archived=False).all()

        for habit in habits:
            last_log = (
                HabitLog.query
                .filter_by(habit_id=habit.id)
                .order_by(HabitLog.completed_date.desc())
                .first()
            )

            if last_log is None or last_log.completed_date < two_days_ago:
                logger.warning(
                    f"[Slip Detection] Habit '{habit.name}' "
                    f"(id={habit.id}, user={habit.user_id}) "
                    f"hasn't been checked in since "
                    f"{last_log.completed_date if last_log else 'never'}."
                )


def start_scheduler(app):
    """
    Start the APScheduler background scheduler.
    Call this from create_app() after blueprints are registered.
    """
    scheduler = BackgroundScheduler()

    # Score recalc — every day at midnight
    scheduler.add_job(
        func=recalculate_all_scores,
        trigger=CronTrigger(hour=0, minute=0),
        args=[app],
        id="recalculate_scores",
        name="Recalculate habit scores nightly",
        replace_existing=True,
    )

    # Slip detection — every day at 8am
    scheduler.add_job(
        func=detect_slipping_habits,
        trigger=CronTrigger(hour=8, minute=0),
        args=[app],
        id="slip_detection",
        name="Detect slipping habits",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("[Scheduler] Started — score recalc at midnight, slip detection at 8am.")
    return scheduler
