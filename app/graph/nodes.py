from typing import Any, Dict

from app.agents.monitoring_agent import MonitoringAgent
from app.agents.diagnostician import Diagnostician
from app.agents.remediation import RemediationAgent
from app.agents.verify import VerifyAgent

from app.graph.state import SentinelState
from app.safety.guardrails import validate_remediation


# Initialize agents once

monitor_agent = MonitoringAgent()
diagnose_agent = Diagnostician()
remediate_agent = RemediationAgent()
verify_agent_instance = VerifyAgent()


def monitor_node(state: SentinelState) -> Dict[str, Any]:
    """Run the monitoring agent and capture observed resource telemetry."""

    query = state.get("user_query", "")

    result = monitor_agent.invoke(query)

    update: Dict[str, Any] = {
        "monitoring_result": result,
        "current_agent": "monitor",
        "status": "monitored",
    }

    # Extract CPU and memory values from the monitoring response.
    # Supports Markdown formatting such as:
    # **CPU Usage:** 88.5%
    # **Memory Usage:** 92.3%

    import re

    cpu_match = re.search(
        r"CPU\s+Usage\s*[:\-]\s*\**\s*(\d+(?:\.\d+)?)\s*%",
        result,
        re.IGNORECASE,
    )

    memory_match = re.search(
        r"Memory\s+Usage\s*[:\-]\s*\**\s*(\d+(?:\.\d+)?)\s*%",
        result,
        re.IGNORECASE,
    )

    if cpu_match:
        update["cpu_usage"] = float(cpu_match.group(1))

    if memory_match:
        update["memory_usage"] = float(memory_match.group(1))

    return update

def diagnose_node(state: SentinelState) -> Dict[str, Any]:
    """Run the diagnostician agent."""

    query = state.get("user_query", "")
    monitoring_result = state.get("monitoring_result", "")

    prompt = f"""
User request:
{query}

Monitoring result:
{monitoring_result}

Based on the current monitoring evidence, diagnose the infrastructure issue.
"""

    result = diagnose_agent.invoke(prompt)

    return {
        "diagnosis_result": result,
        "current_agent": "diagnostician",
        "status": "diagnosed",
    }


def remediate_node(state: SentinelState) -> Dict[str, Any]:
    """
    Run the remediation agent and validate its recommendation
    through Sentinel safety guardrails.
    """

    query = state.get("user_query", "")
    monitoring_result = state.get("monitoring_result", "")
    diagnosis_result = state.get("diagnosis_result", "")

    prompt = f"""
User request:
{query}

Observed monitoring telemetry:
{monitoring_result}

Diagnosis:
{diagnosis_result}

Based on the available evidence, recommend safe, evidence-based
remediation.

Do not execute any remediation action.

Clearly identify:
- Observed issue
- Recommended action
- Priority
- Risk / potential impact
- Approval requirement
- Verification step

If the root cause is uncertain, recommend investigation before
any disruptive remediation.
"""

    result = remediate_agent.invoke(prompt)

    # ------------------------------------------------------------------
    # Safety Guardrail Validation
    # ------------------------------------------------------------------

    # Extract resource information from state when available.
    # The guardrail should use observed telemetry rather than
    # hard-coded values.
    telemetry = {
        "cpu": state.get("cpu_usage"),
        "memory": state.get("memory_usage"),
    }

    validation = validate_remediation(
        result,
        telemetry,
    )

    # Add explicit safety information to the remediation result.
    if validation.get("requires_approval"):
        result += (
            "\n\n### Safety Guardrail\n"
            f"Human approval is required before executing this "
            f"remediation.\n"
            f"Reason: {validation.get('reason', 'Disruptive action detected.')}"
        )

    elif not validation.get("allowed", True):
        result += (
            "\n\n### Safety Guardrail\n"
            "This remediation recommendation is not approved for "
            "automatic execution.\n"
            f"Reason: {validation.get('reason', 'Safety policy violation.')}"
        )

    else:
        result += (
            "\n\n### Safety Guardrail\n"
            "Remediation recommendation passed Sentinel safety validation."
        )

    return {
        "remediation_result": result,
        "current_agent": "remediation",
        "status": "remediation_validated",
        "remediation_validation": validation,
    }


def verify_node(state: SentinelState) -> Dict[str, Any]:
    """Run the verification agent."""

    query = state.get("user_query", "")
    remediation_result = state.get("remediation_result", "")
    monitoring_result = state.get("monitoring_result", "")

    prompt = f"""
User request:
{query}

Current monitoring telemetry:
{monitoring_result}

Previous remediation recommendation:
{remediation_result}

Verify the current infrastructure state using the available telemetry.

Determine whether the issue is:

- RESOLVED
- PARTIALLY_RESOLVED
- NOT_RESOLVED
- INSUFFICIENT_EVIDENCE

Important:
The remediation recommendation was NOT automatically executed.
It must be treated as a recommendation only.

If the issue is not resolved, recommend returning to the Diagnostician.
"""

    result = verify_agent_instance.invoke(prompt)

    return {
        "verification_result": result,
        "current_agent": "verify",
        "status": "verified",
    }