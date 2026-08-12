import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "system_telemetry.db"


def get_connection():
    """Create a connection to the Sentinel telemetry database."""
    return sqlite3.connect(DB_PATH)


def test_connection():
    """Test that the database is accessible."""
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM servers
        """)

        server_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM logs
        """)

        log_count = cursor.fetchone()[0]

        return {
            "servers": server_count,
            "logs": log_count
        }

    finally:
        conn.close()


if __name__ == "__main__":
    print("Database:", DB_PATH)
    print("Status:", test_connection())