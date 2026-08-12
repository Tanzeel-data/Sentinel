import subprocess
from typing import Any, Dict

from app.safety.guardrails import is_safe_command


def execute_system_command(command: str) -> Dict[str, Any]:
    """
    Execute a restricted system diagnostic command.

    All command safety decisions are delegated to the centralized
    Sentinel guardrails module.
    """

    if not command or not command.strip():
        return {
            "success": False,
            "error": "Command cannot be empty.",
        }

    command = command.strip()

    # ---------------------------------------------------------
    # CENTRALIZED SAFETY VALIDATION
    # ---------------------------------------------------------

    safety_check = is_safe_command(command)

    if not safety_check.get("safe", False):
        return {
            "success": False,
            "command": command,
            "error": safety_check.get(
                "reason",
                "Command rejected by safety guardrails.",
            ),
            "requires_approval": safety_check.get(
                "requires_approval",
                True,
            ),
        }

    # ---------------------------------------------------------
    # EXECUTE APPROVED SAFE COMMAND
    # ---------------------------------------------------------

    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        return {
            "success": result.returncode == 0,
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "requires_approval": False,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "command": command,
            "error": "Command timed out after 10 seconds.",
        }

    except Exception as exc:
        return {
            "success": False,
            "command": command,
            "error": str(exc),
        }