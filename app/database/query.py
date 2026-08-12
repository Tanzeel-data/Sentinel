from .connection import get_connection


def get_servers():
    """Return all servers."""
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                server_id,
                hostname,
                region,
                status,
                cpu_usage_percent,
                memory_usage_percent
            FROM servers
            ORDER BY hostname
        """)

        return cursor.fetchall()

    finally:
        conn.close()


def get_recent_logs(limit=20):
    """Return the most recent logs."""
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                log_id,
                server_id,
                timestamp,
                log_level,
                message,
                service_name
            FROM logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

    finally:
        conn.close()


def get_logs_by_level(log_level, limit=50):
    """Return logs matching a specific log level."""
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                log_id,
                server_id,
                timestamp,
                log_level,
                message,
                service_name
            FROM logs
            WHERE log_level = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (log_level, limit))

        return cursor.fetchall()

    finally:
        conn.close()

def get_all_logs():
    """Return all telemetry logs."""
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                log_id,
                server_id,
                timestamp,
                log_level,
                message,
                service_name
            FROM logs
            ORDER BY log_id
        """)

        return cursor.fetchall()

    finally:
        conn.close()
        
if __name__ == "__main__":
    print("\n=== SERVERS ===")

    for server in get_servers():
        print(server)

    print("\n=== RECENT LOGS ===")

    for log in get_recent_logs(5):
        print(log)

    print("\n=== ERROR LOGS ===")

    for log in get_logs_by_level("ERROR", 5):
        print(log)