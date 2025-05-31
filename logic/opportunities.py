from config.db_config import get_connection

def create_opportunity(org_id, data):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO opportunities (title, description, city, date, organization_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["title"],
            data["description"],
            data["city"],
            data["date"],
            org_id
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return True, "Успешно добавлено"

    except Exception as e:
        return False, str(e)


def get_all_opportunities():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT o.title, o.description, o.city, o.date, org.name, org.profile_picture
            FROM opportunities o
            JOIN organizations org ON o.organization_id = org.id
            ORDER BY o.date ASC
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "title": row[0],
                "description": row[1],
                "city": row[2],
                "date": row[3],
                "org": row[4],
                "profile_picture": row[5]
            })
        return result

    except Exception as e:
        print("Ошибка загрузки возможностей:", e)
        return []
