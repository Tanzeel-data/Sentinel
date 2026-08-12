from app.tools.monitoring import (
    get_server_status,
    get_recent_logs,
    get_error_logs,
    get_log_summary,
)


def main():
    print("\n=== SERVER STATUS ===")
    result = get_server_status()

    print("Columns:", result["columns"])
    for row in result["rows"]:
        print(row)

    print("\n=== RECENT LOGS ===")
    result = get_recent_logs(5)

    print("Columns:", result["columns"])
    for row in result["rows"]:
        print(row)

    print("\n=== ERROR LOGS ===")
    result = get_error_logs(5)

    print("Columns:", result["columns"])
    for row in result["rows"]:
        print(row)

    print("\n=== LOG SUMMARY ===")
    result = get_log_summary()

    print("Columns:", result["columns"])
    for row in result["rows"]:
        print(row)


if __name__ == "__main__":
    main()