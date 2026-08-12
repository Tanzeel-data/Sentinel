import re

from .connection import get_connection


ALLOWED_TABLES = {"servers", "logs"}


def validate_sql(sql: str) -> str:
    """
    Validate that a generated SQL statement is read-only
    and only accesses approved Sentinel tables.
    """

    sql = sql.strip()

    # Remove trailing semicolon
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    # Only allow SELECT statements
    if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    # Block dangerous SQL operations
    blocked_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "REPLACE",
        "ATTACH",
        "DETACH",
        "PRAGMA",
        "VACUUM",
    ]

    for keyword in blocked_keywords:
        if re.search(rf"\b{keyword}\b", sql, re.IGNORECASE):
            raise ValueError(
                f"SQL operation '{keyword}' is not allowed."
            )

    # Find table references
    table_matches = re.findall(
        r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)",
        sql,
        re.IGNORECASE,
    )

    for table in table_matches:
        if table.lower() not in ALLOWED_TABLES:
            raise ValueError(
                f"Access to table '{table}' is not allowed."
            )

    return sql


def execute_safe_sql(sql: str):
    """Validate and execute a read-only SQL query."""

    validated_sql = validate_sql(sql)

    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(validated_sql)

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchall()

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
        }

    finally:
        conn.close()


if __name__ == "__main__":
    query = """
        SELECT
            server_id,
            hostname,
            cpu_usage_percent,
            memory_usage_percent
        FROM servers
        ORDER BY cpu_usage_percent DESC
    """

    result = execute_safe_sql(query)

    print("\nColumns:")
    print(result["columns"])

    print("\nRows:")

    for row in result["rows"]:
        print(row)

    print("\nRow count:")
    print(result["row_count"])
    