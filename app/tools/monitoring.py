from typing import Any, Dict

from langchain_core.tools import tool

from app.database.safe_sql import execute_safe_sql


@tool
def get_server_status() -> Dict[str, Any]:
    """
    Get the current status and resource usage of all monitored servers.
    Use this when the user asks about server health, CPU, memory,
    server status, hostname, region, or infrastructure status.
    """

    sql = """
        SELECT
            server_id,
            hostname,
            region,
            status,
            cpu_usage_percent,
            memory_usage_percent
        FROM servers
        ORDER BY server_id
    """

    return execute_safe_sql(sql)


@tool
def get_recent_logs(limit: int = 20) -> Dict[str, Any]:
    """
    Get the most recent system logs.
    Use this when the user asks about recent events, recent activity,
    or what has happened recently.
    """

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


@tool
def get_error_logs(limit: int = 20) -> Dict[str, Any]:
    """
    Get the most recent ERROR-level logs.
    Use this when the user asks about errors, failures, incidents,
    or error activity.
    """

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
        WHERE log_level = 'ERROR'
        ORDER BY timestamp DESC
        LIMIT {limit}
    """

    return execute_safe_sql(sql)


@tool
def get_log_summary() -> Dict[str, Any]:
    """
    Get a summary of logs grouped by severity and service.
    Use this when the user asks for log statistics, counts,
    severity distribution, or service-level log activity.
    """

    sql = """
        SELECT
            log_level,
            service_name,
            COUNT(*) AS count
        FROM logs
        GROUP BY log_level, service_name
        ORDER BY count DESC
    """

    return execute_safe_sql(sql)