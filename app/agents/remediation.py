import logging
import re
from typing import Any, Dict, List

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from app.genai.client import get_gemini_client
from app.tools.registry import get_tools
from app.safety.guardrails import validate_remediation

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are Sentinel, an AI infrastructure remediation agent.

Your job is to recommend safe, evidence-based remediation actions
for infrastructure issues identified from Sentinel telemetry.

You have access to tools that provide:

- Current server status and resource usage
- Recent system logs
- ERROR-level logs
- Log summaries
- Servers with high CPU or memory usage
- ERROR counts grouped by server and service

Rules:

1. Base every remediation recommendation on observed telemetry.

2. Never invent infrastructure state, incidents, metrics, logs,
   causes, or successful remediation actions.

3. Do NOT execute remediation actions. You only recommend them.

4. Clearly distinguish:

   - Observed issue
   - Recommended action
   - Priority
   - Risk or potential impact
   - Approval requirement
   - Verification step

5. Do not recommend destructive or disruptive actions unless the
   available evidence justifies them.

6. For production infrastructure, prefer investigation and
   reversible actions before disruptive actions such as restarting
   services or servers.

7. Do not claim that an action will fix the issue unless the
   telemetry provides sufficient evidence.

8. If the root cause is uncertain, recommend additional investigation
   before taking a disruptive remediation action.

9. Never claim that remediation has already been performed.

10. When multiple issues exist, prioritize the issue with the
    greatest operational risk.

11. Clearly state when human approval is required.

12. Keep responses concise, practical, and useful for infrastructure
    engineers.

13. Every recommendation must include a verification step so that
    engineers can determine whether the remediation was effective.

14. Never execute commands, restart services, reboot servers,
    terminate processes, modify configuration, or change database
    state.

15. Any disruptive remediation recommendation must explicitly state
    that human approval is required.
"""


class RemediationAgent:
    """
    Sentinel agent responsible for recommending safe remediation
    actions based on infrastructure telemetry.

    Remediation actions are NEVER executed by this agent.
    Recommendations are additionally checked by Sentinel guardrails.
    """

    def __init__(self):
        self.client = get_gemini_client()
        self.tools: List[BaseTool] = get_tools()

        logger.info(
            "Remediation agent initialized with %d tools.",
            len(self.tools),
        )

    def _create_agent(self, model_name: str):
        """
        Create a LangChain remediation agent using the specified
        Gemini model.
        """

        logger.info(
            "Creating remediation agent with model: %s",
            model_name,
        )

        return create_agent(
            model=f"google_genai:{model_name}",
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    @staticmethod
    def _extract_response(result) -> str:
        """
        Extract plain text from a LangChain agent result.
        """

        messages = result.get("messages", [])

        if not messages:
            raise RuntimeError("Agent returned no messages.")

        final_message = messages[-1]
        content = final_message.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []

            for part in content:
                if (
                    isinstance(part, dict)
                    and part.get("type") == "text"
                ):
                    text_parts.append(part.get("text", ""))

            return "".join(text_parts)

        return str(content)

    @staticmethod
    def _extract_telemetry(message: str) -> Dict[str, Any]:
        """
        Extract known CPU and memory values from the agent prompt.

        This is intentionally conservative. If values cannot be found,
        no telemetry values are assumed.
        """

        telemetry: Dict[str, Any] = {}

        cpu_match = re.search(
            r"CPU(?:\s+Usage)?[:\s]+[`*]*([0-9]+(?:\.[0-9]+)?)\s*%",
            message,
            re.IGNORECASE,
        )

        memory_match = re.search(
            r"Memory(?:\s+Usage)?[:\s]+[`*]*([0-9]+(?:\.[0-9]+)?)\s*%",
            message,
            re.IGNORECASE,
        )

        if cpu_match:
            telemetry["cpu"] = float(cpu_match.group(1))

        if memory_match:
            telemetry["memory"] = float(memory_match.group(1))

        return telemetry

    @staticmethod
    def _extract_recommended_action(response: str) -> str:
        """
        Extract the recommended action section when present.

        If no explicit section is found, the full response is passed
        to the safety validator for conservative validation.
        """

        patterns = [
            r"(?is)(?:###\s*)?Recommended Action\s*:?\s*(.*?)(?=\n###|\Z)",
            r"(?is)(?:###\s*)?Recommended Remediation\s*:?\s*(.*?)(?=\n###|\Z)",
            r"(?is)(?:###\s*)?Remediation\s*:?\s*(.*?)(?=\n###|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, response)

            if match:
                return match.group(1).strip()

        return response.strip()

    def _apply_guardrail(
        self,
        response: str,
        original_message: str,
    ) -> str:
        """
        Validate the generated remediation recommendation.

        The guardrail does not execute anything. It determines whether
        the recommendation requires human approval.
        """

        action = self._extract_recommended_action(response)
        telemetry = self._extract_telemetry(original_message)

        validation = validate_remediation(
            action,
            telemetry,
        )

        logger.info(
            "Remediation guardrail result: %s",
            validation,
        )

        # Safe recommendation.
        if validation.get("allowed", False):
            return response

        # Disruptive recommendation.
        approval_required = validation.get(
            "requires_approval",
            True,
        )

        reason = validation.get(
            "reason",
            "Remediation requires human approval.",
        )

        guardrail_notice = (
            "\n\n---\n"
            "### Safety Guardrail\n"
            f"- **Approval Required:** {'YES' if approval_required else 'NO'}\n"
            f"- **Reason:** {reason}\n"
            "- **Execution Status:** Not executed.\n"
        )

        return response + guardrail_notice

    def invoke(self, message: str) -> str:
        """
        Process a remediation request using the configured
        Gemini fallback sequence.

        Generated recommendations are passed through Sentinel
        remediation guardrails before being returned.
        """

        logger.info(
            "Remediation request: %s",
            message,
        )

        errors = []

        for model_name in self.client.models:
            try:
                logger.info(
                    "Trying remediation agent with Gemini model: %s",
                    model_name,
                )

                agent = self._create_agent(model_name)

                result = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": message,
                            }
                        ]
                    }
                )

                response = self._extract_response(result)

                # -------------------------------------------------
                # SAFETY GUARDRAIL
                # -------------------------------------------------

                response = self._apply_guardrail(
                    response,
                    message,
                )

                logger.info(
                    "Remediation agent succeeded using model: %s",
                    model_name,
                )

                return response

            except Exception as exc:
                error_message = str(exc)

                logger.warning(
                    "Remediation model failed: %s | %s",
                    model_name,
                    error_message,
                )

                errors.append(
                    f"{model_name}: {error_message}"
                )

        raise RuntimeError(
            "All configured Gemini models failed for the "
            "remediation agent.\n"
            + "\n".join(errors)
        )