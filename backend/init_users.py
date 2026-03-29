"""
Initialize users table with default users
Workaround for bcrypt compatibility issues
"""
import sqlite3
from pathlib import Path
import hashlib

DATABASE_PATH = Path(__file__).parent / "amis.db"

def simple_hash(password: str) -> str:
    """Simple SHA-256 hash for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_users():
    """Create users table and default users"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL,
            disabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    # Insert default users
    users = [
        ("admin", "admin@amis.com", "System Administrator", simple_hash("admin123"), "admin"),
        ("manager", "manager@amis.com", "Plant Manager", simple_hash("manager123"), "manager"),
        ("operator", "operator@amis.com", "Production Operator", simple_hash("operator123"), "operator"),
    ]

    for user in users:
        cursor.execute("""
            INSERT OR REPLACE INTO users (username, email, full_name, hashed_password, role)
            VALUES (?, ?, ?, ?, ?)
        """, user)

    conn.commit()
    conn.close()

    print("[OK] Users table created")
    print("[OK] Default users created: admin, manager, operator")
    print("\nDefault credentials:")
    print("  admin / admin123")
    print("  manager / manager123")
    print("  operator / operator123")

if __name__ == "__main__":
    init_users()
