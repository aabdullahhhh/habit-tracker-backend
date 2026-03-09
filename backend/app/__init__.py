from flask import Flask
from flask_migrate import Migrate
from app.models.db import db


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///habit_tracker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)

    # Import all models so Flask-Migrate can detect them
    from app.models.user            import User
    from app.models.category        import Category
    from app.models.habit           import Habit
    from app.models.habit_log       import HabitLog
    from app.models.habit_score     import HabitScore
    from app.models.partnership     import Partnership
    from app.models.challenge       import Challenge
    from app.models.challenge_entry import ChallengeEntry

    # ── Blueprints ────────────────────────────────────────────────────────────

    # Phase 0
    from app.routes.auth       import auth_bp
    from app.routes.habits     import habits_bp

    # Phase 1
    from app.routes.logs       import logs_bp
    from app.routes.categories import categories_bp

    # Phase 2
    from app.routes.stats      import stats_bp

    # Phase 3 (uncomment when ready)
    # from app.routes.ai_routes import ai_bp

    # Phase 7 (uncomment when ready)
    # from app.routes.partnerships import partnerships_bp
    # from app.routes.challenges   import challenges_bp

    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(habits_bp,      url_prefix="/api/habits")
    app.register_blueprint(categories_bp,  url_prefix="/api/categories")
    app.register_blueprint(logs_bp,        url_prefix="/api/habits/<int:habit_id>/logs")
    app.register_blueprint(stats_bp,       url_prefix="/api/habits")

    # ── Scheduler ─────────────────────────────────────────────────────────────
    import os
    if os.environ.get("FLASK_RUN_FROM_CLI") != "true":
        from app.utils.scheduler import start_scheduler
        start_scheduler(app)

    return app