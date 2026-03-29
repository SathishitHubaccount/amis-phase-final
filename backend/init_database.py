"""
Initialize AMIS Database with updated schema
"""
import sqlite3

DB_PATH = "amis.db"
SCHEMA_PATH = "schema.sql"

def init_database():
    """Create database from schema file."""
    print("Initializing AMIS database...")

    # Read schema
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    # Create database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Execute schema
    cursor.executescript(schema_sql)

    conn.commit()
    conn.close()

    print(f"Database created successfully: {DB_PATH}")
    print("Schema loaded from: {SCHEMA_PATH}")

if __name__ == "__main__":
    init_database()
