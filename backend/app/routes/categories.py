from flask import Blueprint, request, session
from app.models.db import db
from app.models.category import Category
from app.utils.responses import success, error

categories_bp = Blueprint("categories", __name__)


def get_current_user_id():
    return session.get("user_id")


# POST /api/categories — create a category
@categories_bp.route("/", methods=["POST"])
def create_category():
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    color = (data.get("color") or "#6366f1").strip()

    if not name:
        return error("Category name is required", 400)
    if len(name) > 50:
        return error("Name must be 50 characters or fewer", 400)

    # Prevent duplicate names per user
    existing = Category.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        return error("A category with that name already exists", 409)

    category = Category(user_id=user_id, name=name, color=color)
    db.session.add(category)
    db.session.commit()

    return success("Category created", category.to_dict(), 201)


# GET /api/categories — list all my categories
@categories_bp.route("/", methods=["GET"])
def list_categories():
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    categories = (
        Category.query.filter_by(user_id=user_id)
        .order_by(Category.name)
        .all()
    )
    return success("Categories retrieved", [c.to_dict() for c in categories])


# PATCH /api/categories/<id> — rename or recolor
@categories_bp.route("/<int:category_id>", methods=["PATCH"])
def update_category(category_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return error("Category not found", 404)

    data = request.get_json() or {}

    if "name" in data:
        name = (data["name"] or "").strip()
        if not name:
            return error("Name cannot be empty", 400)
        if len(name) > 50:
            return error("Name must be 50 characters or fewer", 400)
        # Check for duplicate (exclude self)
        duplicate = (
            Category.query.filter_by(user_id=user_id, name=name)
            .filter(Category.id != category_id)
            .first()
        )
        if duplicate:
            return error("A category with that name already exists", 409)
        category.name = name

    if "color" in data:
        category.color = (data["color"] or "#6366f1").strip()

    db.session.commit()
    return success("Category updated", category.to_dict())


# DELETE /api/categories/<id> — delete category
@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    user_id = get_current_user_id()
    if not user_id:
        return error("Not authenticated", 401)

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return error("Category not found", 404)

    # Null out any habits using this category (don't delete habits)
    from app.models.habit import Habit
    Habit.query.filter_by(category_id=category_id, user_id=user_id).update(
        {"category_id": None}
    )

    db.session.delete(category)
    db.session.commit()
    return success("Category deleted")
