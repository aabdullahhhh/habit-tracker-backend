from flask import Flask
from .models.db import db
from .routes.auth import auth_bp
from .routes.habits import habits_bp


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key-change-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///habit_tracker.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if config:
        app.config.update(config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(habits_bp, url_prefix="/api/habits")

    # Create tables on first run
    with app.app_context():
        db.create_all()

    return app
