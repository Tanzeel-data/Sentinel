from typing import Any, Dict, List, TypedDict


class SentinelState(TypedDict, total=False):
    """
    Shared state passed between Sentinel agents and workflow nodes.
    """

    user_query: str

    messages: List[Dict[str, Any]]

    telemetry: Dict[str, Any]

    incidents: List[Dict[str, Any]]

    analysis: str

    recommendations: List[str]

    retrieved_context: List[Dict[str, Any]]