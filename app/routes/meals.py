from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for

from app.services import food_service, meal_service, user_service

bp = Blueprint("meals", __name__)

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]
ITEM_ROWS = 5


@bp.route("/foods")
def food_search():
    term = request.args.get("q", "").strip()
    foods = food_service.search_foods(term) if term else []
    return render_template("meals/foods.html", term=term, foods=foods)


def parse_meal_form(form):
    """Check the submitted form.

    Returns (user_id, meal_date, meal_type, items), or raises ValueError
    with a message that is safe to show the user.
    """
    try:
        user_id = int(form["user_id"])
    except ValueError:
        raise ValueError("Pick who ate this meal.")

    try:
        meal_date = date.fromisoformat(form["meal_date"])
    except ValueError:
        raise ValueError("Enter a valid date.")

    if form["meal_type"] not in MEAL_TYPES:
        raise ValueError("Pick a meal type.")

    items = []
    for row in form["rows"]:
        name = row["name"].strip()
        grams_text = row["grams"].strip()
        if not name and not grams_text:
            continue  # blank row, skip it

        try:
            grams = Decimal(grams_text)
        except InvalidOperation:
            grams = Decimal(0)
        if not grams.is_finite():
            grams = Decimal(0)

        if not name or grams <= 0 or grams > 99999:
            raise ValueError("Each food needs a name and an amount between 0 and 99,999 grams.")
        items.append((name, grams))

    if not items:
        raise ValueError("Add at least one food.")

    return user_id, meal_date, form["meal_type"], items


@bp.route("/meals/new", methods=["GET", "POST"])
def new_meal():
    form = {
        "user_id": "",
        "meal_date": date.today().isoformat(),
        "meal_type": "breakfast",
        "rows": [{"name": "", "grams": ""} for _ in range(ITEM_ROWS)],
    }
    error = None

    if request.method == "POST":
        form["user_id"] = request.form.get("user_id", "")
        form["meal_date"] = request.form.get("meal_date", "")
        form["meal_type"] = request.form.get("meal_type", "")
        names = request.form.getlist("food_name")
        grams = request.form.getlist("grams")
        form["rows"] = [{"name": n, "grams": g} for n, g in zip(names, grams)]

        try:
            user_id, meal_date, meal_type, items = parse_meal_form(form)
            meal_id = meal_service.create_meal(user_id, meal_date, meal_type, items)
            return redirect(url_for("meals.meal_detail", meal_id=meal_id))
        except ValueError as problem:
            error = str(problem)

    return render_template(
        "meals/new.html",
        form=form,
        error=error,
        users=user_service.get_users(),
        meal_types=MEAL_TYPES,
        food_names=food_service.get_food_names(),
    )


@bp.route("/meals/<int:meal_id>")
def meal_detail(meal_id):
    meal = meal_service.get_meal(meal_id)
    if meal is None:
        abort(404)
    return render_template("meals/detail.html", meal=meal)