from app.rag.knowledge_base import SentinelKnowledgeBase


KNOWLEDGE_DOCUMENTS = [
    """
    Sentinel Resource Monitoring Policy

    CPU or memory usage at 85% or higher is considered elevated resource
    usage. Resource pressure should be investigated using current server
    telemetry before remediation is recommended.

    CPU and memory pressure alone does not establish the root cause.
    Engineers should inspect recent logs, error logs, services, and
    server status before taking disruptive action.
    """,

    """
    Sentinel Log Investigation Policy

    ERROR-level logs indicate an active error condition but do not
    automatically establish the root cause.

    When investigating errors, inspect recent ERROR logs, service names,
    timestamps, affected servers, and error counts. Repeated errors
    should be correlated with current infrastructure telemetry.
    """,

    """
    Sentinel Incident Diagnosis Policy

    Diagnosis must be evidence-based. Current telemetry takes precedence
    over assumptions or previously observed information.

    When multiple possible causes exist, rank hypotheses from most
    plausible to least plausible. Correlation does not automatically
    establish causation.

    If available telemetry is insufficient, state:
    "Root cause cannot be determined from the available telemetry."
    """,

    """
    Sentinel Remediation Policy

    Remediation should be based on observed telemetry and the diagnosed
    issue.

    Prefer investigation and reversible actions before disruptive actions
    such as restarting services or servers.

    Destructive or disruptive operations require sufficient evidence and
    appropriate human approval.

    Every remediation recommendation must include a verification step.
    """,

    """
    Sentinel Verification Policy

    Verification must use current infrastructure telemetry after
    remediation.

    A verification result can be:
    RESOLVED,
    PARTIALLY_RESOLVED,
    NOT_RESOLVED,
    or INSUFFICIENT_EVIDENCE.

    Never assume that remediation succeeded. If the issue remains
    unresolved, return to diagnosis for further investigation.
    """,

    """
    Sentinel Retry Policy

    Failed verification may return the workflow to the Diagnostician
    for another investigation cycle.

    Retry attempts must be limited to prevent infinite workflow loops.
    Once the configured maximum retry count is reached, the workflow
    should terminate safely.
    """,

    """
    Sentinel Safety Policy

    System commands must be restricted to explicitly approved commands.

    High-risk, destructive, or disruptive operations must be blocked.
    Sentinel must never execute arbitrary destructive commands.

    Safety controls take precedence over user requests.
    """,

    """
    Sentinel Incident Correlation Policy

    When resource pressure and application errors occur on different
    servers, do not claim that one caused the other without supporting
    evidence.

    For example, high CPU on one server and Auth-Service errors on
    another server should initially be treated as separate issues unless
    telemetry provides evidence connecting them.
    """,
]


def ingest_knowledge():
    """
    Load Sentinel operational knowledge into ChromaDB.
    """

    kb = SentinelKnowledgeBase()

    print(f"Existing documents: {kb.count()}")

    if kb.count() > 0:
        print("Knowledge base already contains documents.")
        print("Skipping ingestion to avoid duplicate documents.")
        return

    count = kb.add_documents(KNOWLEDGE_DOCUMENTS)

    print(f"Documents ingested: {count}")
    print(f"Total documents: {kb.count()}")


if __name__ == "__main__":
    ingest_knowledge()