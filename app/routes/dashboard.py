from datetime import date

from flask import Blueprint, render_template, request

from app.services import food_service, meal_service, user_service

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def home():
    food_count = food_service.count_foods()
    return render_template("dashboard/home.html", food_count=food_count)


@bp.route("/day")
def day_view():
    users = user_service.get_users()

    user_id = request.args.get("user_id", type=int)
    if user_id is None and users:
        user_id = users[0]["user_id"]

    try:
        day = date.fromisoformat(request.args.get("date", ""))
    except ValueError:
        day = date.today()

    data = meal_service.get_day(user_id, day)
    return render_template(
        "dashboard/day.html",
        users=users,
        user_id=user_id,
        day=day.isoformat(),
        totals=data["totals"],
        meals=data["meals"],
    )