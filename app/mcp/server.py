from mcp.server.fastmcp import FastMCP

from app.mcp.tools.logs import get_system_logs
from app.mcp.tools.commands import execute_system_command
from app.mcp.tools.knowledge import query_knowledge_base
from app.mcp.tools.database import query_database


# Create Sentinel MCP server
mcp = FastMCP("Sentinel")


# Register Sentinel MCP tools
mcp.tool()(get_system_logs)
mcp.tool()(execute_system_command)
mcp.tool()(query_knowledge_base)
mcp.tool()(query_database)


if __name__ == "__main__":
    mcp.run()