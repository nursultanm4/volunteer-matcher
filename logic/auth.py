import psycopg2
from config.db_config import get_connection

def register_user(role, name, phone, password):
    conn = get_connection()
    cursor = conn.cursor()

    if len(password) < 8:
        conn.close()
        return False, "Пароль должен содержать минимум 8 символов."

    table = "volunteers" if role == "volunteer" else "organizations"

    cursor.execute(f"SELECT * FROM {table} WHERE phone = %s;", (phone,))
    if cursor.fetchone():
        conn.close()
        return False, "Пользователь с таким номером уже существует."

    cursor.execute(
        f"""INSERT INTO {table} (name, phone, password) 
            VALUES (%s, %s, %s) RETURNING id, name;""",
        (name, phone, password)
    )
    user = cursor.fetchone()
    conn.commit()
    conn.close()
    return True, {"id": user[0], "name": user[1], "role": role}


def login_user(role, phone, password):
    if not phone or not password:
        return False, "Поля не должны быть пустыми."

    if role not in ("volunteer", "organization"):
        return False, "Некорректная роль."

    conn = get_connection()
    cursor = conn.cursor()

    table = "volunteers" if role == "volunteer" else "organizations"

    cursor.execute(
        f"SELECT id, name FROM {table} WHERE phone = %s AND password = %s;",
        (phone, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return True, {"id": user[0], "name": user[1], "role": role}
    return False, "Неверный номер или пароль."


def update_user_profile(role, user_id, data):
    table = "volunteers" if role == "volunteer" else "organizations"

    columns = []
    values = []
    for key, value in data.items():
        if value:
            columns.append(f"{key} = %s")
            values.append(value)

    if not columns:
        return

    values.append(user_id)

    query = f"""
        UPDATE {table}
        SET {', '.join(columns)}
        WHERE id = %s
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
    except Exception as e:
        print("Ошибка при обновлении профиля:", e)
    finally:
        cursor.close()
        conn.close()


def get_user_profile(role, user_id):
    table = "volunteers" if role == "volunteer" else "organizations"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            colnames = [desc[0] for desc in cursor.description]
            return dict(zip(colnames, row))
    except Exception as e:
        print("Ошибка при загрузке профиля:", e)
    finally:
        cursor.close()
        conn.close()
    return {}
