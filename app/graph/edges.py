from typing import Literal

from app.graph.state import SentinelState


def monitor_to_diagnose(
    state: SentinelState,
) -> Literal["diagnose"]:
    """Route Monitor to Diagnostician."""
    return "diagnose"


def diagnose_to_remediate(
    state: SentinelState,
) -> Literal["remediate"]:
    """Route Diagnostician to Remediation."""
    return "remediate"


def remediate_to_verify(
    state: SentinelState,
) -> Literal["verify"]:
    """Route Remediation to Verification."""
    return "verify"


def verify_router(
    state: SentinelState,
) -> Literal["diagnose", "end"]:
    """
    Route based on verification result.

    If the issue is unresolved, return to Diagnostician.
    If resolved, terminate the workflow.
    """

    verification_result = state.get(
        "verification_result",
        "",
    )

    result = str(verification_result).upper()

    if (
        "NOT_RESOLVED" in result
        or "PARTIALLY_RESOLVED" in result
    ):
        return "diagnose"

    if "RESOLVED" in result:
        return "end"

    # If verification is inconclusive,
    # send it back for further investigation.
    return "diagnose"