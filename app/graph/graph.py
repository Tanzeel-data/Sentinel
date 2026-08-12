from langgraph.graph import StateGraph, START, END

from app.graph.state import SentinelState
from app.graph.nodes import (
    monitor_node,
    diagnose_node,
    remediate_node,
    verify_node,
)


def build_sentinel_graph():
    """
    Build the Sentinel infrastructure investigation
    and remediation recommendation workflow.
    """

    graph = StateGraph(SentinelState)

    # ---------------------------------------------------------
    # Register nodes
    # ---------------------------------------------------------

    graph.add_node("monitor", monitor_node)
    graph.add_node("diagnostician", diagnose_node)
    graph.add_node("remediation", remediate_node)
    graph.add_node("verify", verify_node)

    # ---------------------------------------------------------
    # Workflow edges
    # ---------------------------------------------------------

    graph.add_edge(START, "monitor")

    graph.add_edge("monitor", "diagnostician")

    graph.add_edge("diagnostician", "remediation")

    graph.add_edge("remediation", "verify")

    graph.add_edge("verify", END)

    # ---------------------------------------------------------
    # Compile graph
    # ---------------------------------------------------------

    return graph.compile()


# Compiled Sentinel workflow
sentinel_graph = build_sentinel_graph()