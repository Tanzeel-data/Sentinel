"""
Sentinel Safety Guardrails

Deterministic safety checks for:
- System commands
- SQL queries
- Remediation actions
- Evidence-based remediation recommendations

The guardrails validate actions but never execute them.
"""

import re
from typing import Any, Dict


# ---------------------------------------------------------------------
# Dangerous system commands
# ---------------------------------------------------------------------

DANGEROUS_COMMAND_PATTERNS = [
    r"\breboot\b",
    r"\bshutdown\b",
    r"\bpoweroff\b",
    r"\bstop-service\b",
    r"\bkill\b",
    r"\bkillall\b",
    r"\btaskkill\b",
    r"\bformat\b",
    r"\brm\s+-rf\b",
    r"\bdel\s+/[sfq]\b",
    r"\bremove-item\b",
    r"\bsc\s+(stop|delete)\b",
    r"\bnet\s+stop\b",
]


# ---------------------------------------------------------------------
# Dangerous SQL operations
# ---------------------------------------------------------------------

DANGEROUS_SQL_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bREPLACE\b",
    r"\bMERGE\b",
]


# ---------------------------------------------------------------------
# Disruptive remediation actions
# ---------------------------------------------------------------------

DISRUPTIVE_ACTION_PATTERNS = [
    r"\brestart\b",
    r"\breboot\b",
    r"\bshutdown\b",
    r"\bpower\s*off\b",
    r"\bstop\b",
    r"\bkill\b",
    r"\bterminate\b",
    r"\bdelete\b",
    r"\bremove\b",
    r"\bdisable\b",
]


# ---------------------------------------------------------------------
# Generic helper
# ---------------------------------------------------------------------

def _matches_any(text: str, patterns: list[str]) -> bool:
    """Return True if text matches any supplied regex pattern."""

    if not isinstance(text, str):
        return False

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


# ---------------------------------------------------------------------
# Command safety
# ---------------------------------------------------------------------

def is_safe_command(command: str) -> Dict[str, Any]:
    """
    Validate a system command.

    Read-only diagnostic commands are allowed.

    Potentially destructive, disruptive, or shell-injection
    commands are blocked and require human approval.
    """

    if not isinstance(command, str) or not command.strip():
        return {
            "safe": False,
            "requires_approval": True,
            "reason": "Command is empty or invalid.",
        }

    command = command.strip()

    # Block shell chaining, piping, redirection, command substitution,
    # and other shell-injection operators.
    dangerous_operators = [
        ";",
        "&",
        "|",
        ">",
        "<",
        "`",
        "$(",
        "${",
    ]

    for operator in dangerous_operators:
        if operator in command:
            return {
                "safe": False,
                "requires_approval": True,
                "command": command,
                "reason": (
                    "Command contains unsupported or potentially "
                    "dangerous shell operators."
                ),
            }

    # Check existing dangerous command patterns.
    if _matches_any(command, DANGEROUS_COMMAND_PATTERNS):
        return {
            "safe": False,
            "requires_approval": True,
            "command": command,
            "reason": "Command is potentially disruptive or destructive.",
        }

    return {
        "safe": True,
        "requires_approval": False,
        "command": command,
        "reason": "Command appears to be a non-destructive diagnostic command.",
    }

# ---------------------------------------------------------------------
# SQL safety
# ---------------------------------------------------------------------

def is_safe_query(query: str) -> Dict[str, Any]:
    """
    Validate an SQL query.

    Only SELECT and WITH queries are considered safe.

    INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE and other write/
    schema-changing operations are blocked.
    """

    if not isinstance(query, str) or not query.strip():
        return {
            "safe": False,
            "requires_approval": True,
            "reason": "SQL query is empty or invalid.",
        }

    query = query.strip()

    # Remove leading SQL comments before checking the statement.
    cleaned_query = re.sub(
        r"^\s*(--.*?\n|/\*.*?\*/)*",
        "",
        query,
        flags=re.DOTALL,
    ).strip()

    # Sentinel database policy: only SELECT/WITH queries are allowed.
    if not re.match(r"^(SELECT|WITH)\b", cleaned_query, re.IGNORECASE):
        return {
            "safe": False,
            "requires_approval": True,
            "query": query,
            "reason": "Only read-only SELECT or WITH queries are allowed.",
        }

    # Additional protection against embedded write operations.
    if _matches_any(cleaned_query, DANGEROUS_SQL_PATTERNS):
        return {
            "safe": False,
            "requires_approval": True,
            "query": query,
            "reason": "Query contains a potentially destructive SQL operation.",
        }

    return {
        "safe": True,
        "requires_approval": False,
        "query": query,
        "reason": "Read-only SQL query accepted.",
    }


# ---------------------------------------------------------------------
# Remediation safety
# ---------------------------------------------------------------------

def requires_approval(action: str) -> bool:
    """
    Determine whether a remediation action requires human approval.

    Any disruptive action requires explicit approval.
    """

    if not isinstance(action, str) or not action.strip():
        return True

    return _matches_any(
        action,
        DISRUPTIVE_ACTION_PATTERNS,
    )


# ---------------------------------------------------------------------
# Evidence validation
# ---------------------------------------------------------------------

def validate_remediation(
    action: str,
    evidence: Any,
) -> Dict[str, Any]:
    """
    Validate whether a remediation recommendation is sufficiently
    supported by available evidence.

    Disruptive actions require human approval regardless of evidence.
    """

    if not isinstance(action, str) or not action.strip():
        return {
            "allowed": False,
            "requires_approval": True,
            "reason": "No remediation action was provided.",
        }

    if evidence is None or evidence == "":
        return {
            "allowed": False,
            "requires_approval": True,
            "reason": "Remediation cannot be recommended without evidence.",
        }

    disruptive = requires_approval(action)

    if disruptive:
        return {
            "allowed": False,
            "requires_approval": True,
            "action": action,
            "reason": (
                "Disruptive remediation requires explicit human approval."
            ),
        }

    return {
        "allowed": True,
        "requires_approval": False,
        "action": action,
        "reason": "Action is non-disruptive and has supporting evidence.",
    }


# ---------------------------------------------------------------------
# Combined safety check
# ---------------------------------------------------------------------

def check_action(
    action_type: str,
    action: str,
    evidence: Any = None,
) -> Dict[str, Any]:
    """
    Central safety entry point.

    Supported action types:
        - command
        - query
        - remediation
    """

    action_type = action_type.lower().strip()

    if action_type == "command":
        return is_safe_command(action)

    if action_type == "query":
        return is_safe_query(action)

    if action_type == "remediation":
        return validate_remediation(action, evidence)

    return {
        "safe": False,
        "allowed": False,
        "requires_approval": True,
        "reason": f"Unknown action type: {action_type}",
    }