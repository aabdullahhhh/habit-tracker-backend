from flask import jsonify


# ── Structured JSON response helpers ──────────────────────────────────────────

def success(data=None, message="Success", status=200):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error(message="An error occurred", status=400, errors=None):
    payload = {"success": False, "message": message}
    if errors:
        payload["errors"] = errors
    return jsonify(payload), status


# ── Input validation helpers ───────────────────────────────────────────────────

def validate_required(body: dict, fields: list[str]) -> list[str]:
    """Return a list of missing or empty required field names."""
    return [f for f in fields if not body.get(f, "").strip()]


def validate_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]
