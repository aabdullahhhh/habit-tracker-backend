from flask import Blueprint, request, session
from werkzeug.security import generate_password_hash, check_password_hash

from ..models.db import db
from ..models.user import User
from ..utils.responses import success, error, validate_required, validate_email

auth_bp = Blueprint("auth", __name__)


# POST /api/auth/register
@auth_bp.route("/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}

    # Validate required fields
    missing = validate_required(body, ["username", "email", "password"])
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400)

    if not validate_email(body["email"]):
        return error("Invalid email address.", 400)

    if len(body["password"]) < 6:
        return error("Password must be at least 6 characters.", 400)

    # Check uniqueness
    if User.query.filter_by(username=body["username"].strip()).first():
        return error("Username already taken.", 409)
    if User.query.filter_by(email=body["email"].strip().lower()).first():
        return error("Email already registered.", 409)

    user = User(
        username=body["username"].strip(),
        email=body["email"].strip().lower(),
        password_hash=generate_password_hash(body["password"]),
    )
    db.session.add(user)
    db.session.commit()

    return success(user.to_dict(), "User registered successfully.", 201)


# POST /api/auth/login
@auth_bp.route("/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}

    missing = validate_required(body, ["email", "password"])
    if missing:
        return error(f"Missing required fields: {', '.join(missing)}", 400)

    user = User.query.filter_by(email=body["email"].strip().lower()).first()
    if not user or not check_password_hash(user.password_hash, body["password"]):
        return error("Invalid email or password.", 401)

    # Store user id in session (replace with JWT later)
    session["user_id"] = user.id

    return success(user.to_dict(), "Login successful.")


# POST /api/auth/logout
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return success(message="Logged out successfully.")


# GET /api/auth/me  – handy helper to check current session
@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return error("Not authenticated.", 401)
    user = db.session.get(User, user_id)
    if not user:
        return error("User not found.", 404)
    return success(user.to_dict())
