import pandas as pd

from app.db import get_connection

CSV_FILE = "data/foods_clean.csv"

INSERT_SQL = """
    INSERT INTO foods (name, calories_per_100g, protein_g, carbs_g, fat_g)
    VALUES (%s, %s, %s, %s, %s)
"""


def load_foods():
    foods = pd.read_csv(CSV_FILE)
    rows = foods.values.tolist()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM foods")
            if cur.fetchone()["n"] > 0:
                print("The foods table already has rows, so nothing was loaded.")
                return
            cur.executemany(INSERT_SQL, rows)
        conn.commit()
        print(f"Loaded {len(rows)} foods.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    load_foods()