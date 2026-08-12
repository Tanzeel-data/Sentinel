from typing import Any, Dict, Optional
from typing_extensions import TypedDict


class SentinelState(TypedDict, total=False):
    # User request / incident context
    user_query: str
    incident_id: Optional[str]

    # Agent outputs
    monitoring_result: Any
    diagnosis_result: Any
    remediation_result: Any
    verification_result: Any

    # Observed telemetry
    cpu_usage: Optional[float]
    memory_usage: Optional[float]

    # Safety validation
    remediation_validation: Dict[str, Any]

    # Workflow control
    current_agent: str
    status: str
    retry_count: int
    max_retries: int

    # Final workflow information
    error: Optional[str]
    final_result: Optional[str]