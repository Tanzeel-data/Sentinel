import logging

from app.agents.monitoring_agent import MonitoringAgent
from app.agents.incident_analysis_agent import IncidentAnalysisAgent


logger = logging.getLogger(__name__)


class SentinelRouter:
    """
    Routes user requests to the appropriate Sentinel agent.

    MonitoringAgent:
        Handles server status, resources, logs, errors, and telemetry.

    IncidentAnalysisAgent:
        Handles incident investigation, relationships between issues,
        prioritization, impact, causes, and recommendations.
    """

    def __init__(self):
        self.monitoring_agent = MonitoringAgent()
        self.incident_agent = IncidentAnalysisAgent()

        logger.info("Sentinel router initialized.")

    def _route(self, query: str) -> str:
        """
        Determine which agent should handle the query.
        """

        text = query.lower()

        incident_keywords = [
            "incident",
            "root cause",
            "cause",
            "impact",
            "relationship",
            "related",
            "correlation",
            "correlate",
            "most important",
            "most critical",
            "priority",
            "prioritize",
            "investigate",
            "investigation",
            "why",
            "risk",
            "recommend",
            "recommendation",
        ]

        for keyword in incident_keywords:
            if keyword in text:
                return "incident"

        return "monitoring"

    def invoke(self, query: str) -> str:
        """
        Route a user query to the appropriate Sentinel agent.
        """

        logger.info(
            "Routing Sentinel request: %s",
            query,
        )

        route = self._route(query)

        logger.info(
            "Selected route: %s",
            route,
        )

        if route == "incident":
            return self.incident_agent.invoke(query)

        return self.monitoring_agent.invoke(query)