import psycopg2
import sys
sys.path.append('') # PUT YOUR PATH to the project root here
from db_config import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            password TEXT NOT NULL CHECK (char_length(password) >= 8),
            phone VARCHAR(15),
            city TEXT,
            description TEXT,
            profile_picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS volunteers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            password TEXT NOT NULL CHECK (char_length(password) >= 8),
            phone VARCHAR(15),
            skills TEXT,
            profile_picture TEXT,
            availability TEXT,
            city VARCHAR(100),
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            age VARCHAR(3)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            profile_picture TEXT,
            city TEXT NOT NULL,
            date DATE NOT NULL,
            organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            volunteer_id INTEGER REFERENCES volunteers(id) ON DELETE CASCADE,
            opportunity_id INTEGER REFERENCES opportunities(id) ON DELETE CASCADE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunity_views (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            user_role VARCHAR(20) NOT NULL,
            opportunity_id INTEGER REFERENCES opportunities(id) ON DELETE CASCADE,
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, user_role, opportunity_id)
        );
        """)

        cursor.execute("""
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS skills TEXT;
        """)

        conn.commit()
        print("✅Все таблицы созданы")

    except Exception as e:
        print("❌ Ошибка при создании таблиц:", e)
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
