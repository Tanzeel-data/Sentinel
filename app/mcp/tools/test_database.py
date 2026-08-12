from app.mcp.tools.database import query_database


sql = """
SELECT
    server_id,
    service_name,
    COUNT(log_id) AS error_count
FROM logs
WHERE log_level = 'ERROR'
GROUP BY server_id, service_name
ORDER BY error_count DESC
"""

print(query_database(sql))