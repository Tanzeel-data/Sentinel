from typing import Any, Dict

from langchain_core.tools import tool

from app.database.safe_sql import execute_safe_sql


@tool
def get_high_resource_servers() -> Dict[str, Any]:
    """
    Get servers with elevated CPU or memory usage.

    Use this when investigating server resource pressure,
    high CPU usage, high memory usage, or infrastructure incidents.
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
        WHERE cpu_usage_percent >= 85
           OR memory_usage_percent >= 85
        ORDER BY
            memory_usage_percent DESC,
            cpu_usage_percent DESC
    """

    return execute_safe_sql(sql)


@tool
def get_error_counts_by_server() -> Dict[str, Any]:
    """
    Get ERROR log counts grouped by server and service.

    Use this when investigating error activity,
    incidents, or failures across monitored infrastructure.
    """

    sql = """
        SELECT
            server_id,
            service_name,
            COUNT(*) AS error_count
        FROM logs
        WHERE log_level = 'ERROR'
        GROUP BY server_id, service_name
        ORDER BY error_count DESC
    """

    return execute_safe_sql(sql)