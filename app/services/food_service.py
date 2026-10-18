from app.db import get_connection


def count_foods():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM foods")
            return cur.fetchone()["n"]
    finally:
        conn.close()

def search_foods(term, limit=50):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT food_id, name, calories_per_100g, protein_g, carbs_g, fat_g
                FROM foods
                WHERE name LIKE %s
                ORDER BY name
                LIMIT %s
                """,
                (f"%{term}%", limit),
            )
            return cur.fetchall()
    finally:
        conn.close()

def get_food_names():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM foods ORDER BY name")
            return [row["name"] for row in cur.fetchall()]
    finally:
        conn.close()