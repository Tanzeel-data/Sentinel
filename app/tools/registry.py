from app.tools.incident_tools import (
    get_high_resource_servers,
    get_error_counts_by_server,
)

from app.tools.monitoring import (
    get_server_status,
    get_recent_logs,
    get_error_logs,
    get_log_summary,
)

# MCP-backed tools
from app.mcp.tools.logs import get_system_logs
from app.mcp.tools.commands import execute_system_command
from app.mcp.tools.knowledge import query_knowledge_base
from app.mcp.tools.database import query_database


def get_tools():
    """Return all Sentinel tools available to the agents."""

    return [
        # Monitoring tools
        get_server_status,
        get_recent_logs,
        get_error_logs,
        get_log_summary,

        # Incident analysis tools
        get_high_resource_servers,
        get_error_counts_by_server,

        # MCP tools
        get_system_logs,
        execute_system_command,
        query_knowledge_base,
        query_database,
    ]