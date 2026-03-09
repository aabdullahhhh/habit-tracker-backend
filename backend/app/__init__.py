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

    # Phase 0
    from app.routes.auth   import auth_bp
    from app.routes.habits import habits_bp

    # Phase 1
    from app.routes.logs       import logs_bp
    from app.routes.categories import categories_bp

    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(habits_bp,      url_prefix="/api/habits")
    app.register_blueprint(categories_bp,  url_prefix="/api/categories")
    app.register_blueprint(logs_bp,        url_prefix="/api/habits/<int:habit_id>/logs")

    return app