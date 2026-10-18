from app.db import get_connection


def get_users():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, username FROM users ORDER BY username")
            return cur.fetchall()
    finally:
        conn.close()