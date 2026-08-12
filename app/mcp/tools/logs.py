from typing import Any, Dict

from app.database.safe_sql import execute_safe_sql


def get_system_logs(limit: int = 20) -> Dict[str, Any]:
    """
    Retrieve recent system logs for Sentinel.

    This MCP tool provides current telemetry from the logs table.
    It is intended for monitoring, diagnosis, and verification.
    """

    # Keep the requested number of logs within a safe range.
    limit = max(1, min(limit, 100))

    sql = f"""
        SELECT
            log_id,
            server_id,
            timestamp,
            log_level,
            message,
            service_name
        FROM logs
        ORDER BY timestamp DESC
        LIMIT {limit}
    """

    return execute_safe_sql(sql)