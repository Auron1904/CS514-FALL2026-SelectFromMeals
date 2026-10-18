from app.db import get_connection


def create_meal(user_id, meal_date, meal_type, items):
    """Save a meal and all of its foods, or save nothing.

    items is a list of (food_name, grams) pairs.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO meals (user_id, meal_date, meal_type) VALUES (%s, %s, %s)",
                (user_id, meal_date, meal_type),
            )
            meal_id = cur.lastrowid

            for food_name, grams in items:
                cur.execute("SELECT food_id FROM foods WHERE name = %s", (food_name,))
                food = cur.fetchone()
                if food is None:
                    raise ValueError(f'"{food_name}" is not in the food list.')
                cur.execute(
                    "INSERT INTO meal_items (meal_id, food_id, quantity_g) VALUES (%s, %s, %s)",
                    (meal_id, food["food_id"], grams),
                )
        conn.commit()
        return meal_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_meal(meal_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT m.meal_id, m.user_id, m.meal_date, m.meal_type, u.username
                FROM meals m
                JOIN users u ON u.user_id = m.user_id
                WHERE m.meal_id = %s
                """,
                (meal_id,),
            )
            meal = cur.fetchone()
            if meal is None:
                return None

            cur.execute(
                """
                SELECT f.name,
                       mi.quantity_g,
                       ROUND(f.calories_per_100g * mi.quantity_g / 100, 1) AS calories,
                       ROUND(f.protein_g * mi.quantity_g / 100, 1) AS protein_g,
                       ROUND(f.carbs_g * mi.quantity_g / 100, 1) AS carbs_g,
                       ROUND(f.fat_g * mi.quantity_g / 100, 1) AS fat_g
                FROM meal_items mi
                JOIN foods f ON f.food_id = mi.food_id
                WHERE mi.meal_id = %s
                ORDER BY mi.meal_item_id
                """,
                (meal_id,),
            )
            meal["entries"] = cur.fetchall()

            cur.execute(
                """
                SELECT calories, protein_g, carbs_g, fat_g
                FROM meal_totals
                WHERE meal_id = %s
                """,
                (meal_id,),
            )
            meal["totals"] = cur.fetchone()
            return meal
    finally:
        conn.close()


def get_day(user_id, meal_date):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT meals, calories, protein_g, carbs_g, fat_g
                FROM daily_totals
                WHERE user_id = %s AND meal_date = %s
                """,
                (user_id, meal_date),
            )
            totals = cur.fetchone()

            cur.execute(
                """
                SELECT meal_id, meal_type, item_count, calories, protein_g, carbs_g, fat_g
                FROM meal_totals
                WHERE user_id = %s AND meal_date = %s
                ORDER BY meal_type, meal_id
                """,
                (user_id, meal_date),
            )
            meals = cur.fetchall()

            return {"totals": totals, "meals": meals}
    finally:
        conn.close()