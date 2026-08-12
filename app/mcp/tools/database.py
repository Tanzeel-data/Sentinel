from typing import Any, Dict

from app.database.safe_sql import execute_safe_sql
from app.safety.guardrails import is_safe_query


def query_database(sql: str) -> Dict[str, Any]:
    """
    Execute a safe, read-only SQL query against the Sentinel database.

    All SQL safety validation is delegated to the centralized guardrails
    module. Only read-only SELECT/WITH queries are permitted.
    """

    if not sql or not sql.strip():
        return {
            "success": False,
            "error": "SQL query cannot be empty.",
        }

    query = sql.strip()

    # Remove a trailing semicolon for validation/execution consistency.
    if query.endswith(";"):
        query = query[:-1].strip()

    # ---------------------------------------------------------
    # CENTRALIZED SAFETY VALIDATION
    # ---------------------------------------------------------

    safety_check = is_safe_query(query)

    if not safety_check.get("safe", False):
        return {
            "success": False,
            "query": query,
            "error": safety_check.get(
                "reason",
                "SQL query rejected by safety guardrails.",
            ),
            "requires_approval": safety_check.get(
                "requires_approval",
                True,
            ),
        }

    # ---------------------------------------------------------
    # EXECUTE SAFE QUERY
    # ---------------------------------------------------------

    try:
        result = execute_safe_sql(query)

        return {
            "success": True,
            "query": query,
            "result": result,
            "requires_approval": False,
        }

    except Exception as exc:
        return {
            "success": False,
            "query": query,
            "error": str(exc),
        }