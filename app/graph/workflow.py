from langgraph.graph import StateGraph, START, END

from app.graph.state import SentinelState
from app.graph.nodes import (
    monitor_node,
    diagnose_node,
    remediate_node,
    verify_node,
)


DEFAULT_MAX_RETRIES = 2


def verification_router(state: SentinelState):
    """
    Decide whether the workflow should finish or retry diagnosis
    after verification.
    """

    verification_result = state.get("verification_result", {})

    # Handle dictionary or string verification results
    if isinstance(verification_result, dict):
        result_text = str(verification_result.get("result", ""))
        status_text = str(verification_result.get("status", ""))
        combined_result = f"{result_text} {status_text}".upper()
    else:
        combined_result = str(verification_result).upper()

    # Check exact successful verification first.
    if (
        "NOT_RESOLVED" not in combined_result
        and "PARTIALLY_RESOLVED" not in combined_result
        and "INSUFFICIENT_EVIDENCE" not in combined_result
        and "RESOLVED" in combined_result
    ):
        return END

    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", DEFAULT_MAX_RETRIES)

    # Stop after maximum retries.
    if retry_count >= max_retries:
        return END

    return "retry"


def increment_retry(state: SentinelState):
    """
    Increment the retry counter before returning to diagnosis.
    """

    retry_count = state.get("retry_count", 0)

    return {
        "retry_count": retry_count + 1,
        "current_agent": "retry",
        "status": "retrying",
    }


def build_workflow():
    """
    Build the Sentinel LangGraph workflow.

    Normal flow:

        START
          ↓
        Monitor
          ↓
        Diagnose
          ↓
        Remediate
          ↓
        Verify
          ↓
        END

    Failed verification:

        Verify
          ↓
        Increment Retry
          ↓
        Diagnose
          ↓
        Remediate
          ↓
        Verify

    The retry loop is limited by max_retries.
    """

    graph = StateGraph(SentinelState)

    # Register nodes
    graph.add_node("monitor", monitor_node)
    graph.add_node("diagnose", diagnose_node)
    graph.add_node("remediate", remediate_node)
    graph.add_node("verify", verify_node)
    graph.add_node("increment_retry", increment_retry)

    # Main workflow
    graph.add_edge(START, "monitor")
    graph.add_edge("monitor", "diagnose")
    graph.add_edge("diagnose", "remediate")
    graph.add_edge("remediate", "verify")

    # Verification decision
    graph.add_conditional_edges(
        "verify",
        verification_router,
        {
            "retry": "increment_retry",
            END: END,
        },
    )

    # Retry → Diagnose
    graph.add_edge("increment_retry", "diagnose")

    return graph.compile()


sentinel_workflow = build_workflow()