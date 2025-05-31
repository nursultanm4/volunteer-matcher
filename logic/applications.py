from config.db_config import get_connection

def apply_to_opportunity(volunteer_id, opportunity_id):
    conn = get_connection()
    cursor = conn.cursor()
    # prevent duplicate applications
    cursor.execute(
        "SELECT 1 FROM applications WHERE volunteer_id = %s AND opportunity_id = %s",
        (volunteer_id, opportunity_id)
    )
    if cursor.fetchone():
        conn.close()
        return False  

    cursor.execute(
        "INSERT INTO applications (volunteer_id, opportunity_id) VALUES (%s, %s)",
        (volunteer_id, opportunity_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True

def get_applications_for_organization(org_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, v.id, v.name, v.profile_picture, o.title, a.opportunity_id, a.seen
        FROM applications a
        JOIN volunteers v ON a.volunteer_id = v.id
        JOIN opportunities o ON a.opportunity_id = o.id
        WHERE o.organization_id = %s
        ORDER BY a.applied_at DESC
    """, (org_id,))
    rows = cursor.fetchall()
    cursor.execute("""
        UPDATE applications SET seen = TRUE
        FROM opportunities o
        WHERE applications.opportunity_id = o.id AND o.organization_id = %s AND applications.seen = FALSE
    """, (org_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return [
        {
            "application_id": row[0],
            "volunteer_id": row[1],
            "volunteer_name": row[2],
            "profile_picture": row[3],
            "opportunity_title": row[4],
            "opportunity_id": row[5],
            "seen": row[6]
        }
        for row in rows
    ]

def has_unseen_applications(org_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1
        FROM applications a
        JOIN opportunities o ON a.opportunity_id = o.id
        WHERE o.organization_id = %s AND a.seen = FALSE
        LIMIT 1
    """, (org_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return bool(result)

def record_opportunity_view(user_id, user_role, opportunity_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO opportunity_views (user_id, user_role, opportunity_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, user_role, opportunity_id) DO NOTHING
            """,
            (user_id, user_role, opportunity_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_opportunity_views(opportunity_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM opportunity_views WHERE opportunity_id = %s",
        (opportunity_id,)
    )
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def get_applications_for_opportunity(opportunity_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT volunteer_id FROM applications WHERE opportunity_id = %s
    """, (opportunity_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"volunteer_id": row[0]} for row in rows]

    