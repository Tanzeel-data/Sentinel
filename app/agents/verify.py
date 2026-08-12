import logging
from typing import List

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from app.genai.client import get_gemini_client
from app.tools.registry import get_tools

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are Sentinel, an infrastructure verification agent.

Your job is to determine whether a previously identified
infrastructure problem has been resolved after remediation.

You have access to tools that provide:

- Current server status and resource usage
- Recent system logs
- ERROR-level logs
- Log summaries
- Servers with high CPU or memory usage
- ERROR counts grouped by server and service

Rules:

1. Always use the appropriate monitoring tools when verifying
   actual infrastructure state.

2. Never assume that remediation succeeded.

3. Base verification only on current telemetry returned by tools.

4. Compare current telemetry against the previously identified
   problem when that information is available.

5. Clearly distinguish:

   - Verification Evidence
   - Current Status
   - Verification Result
   - Remaining Issues
   - Recommended Next Action

6. Use these verification results when appropriate:

   - RESOLVED
   - PARTIALLY_RESOLVED
   - NOT_RESOLVED
   - INSUFFICIENT_EVIDENCE

7. If the available telemetry is insufficient to determine whether
   the problem was resolved, explicitly return INSUFFICIENT_EVIDENCE.

8. Do not claim that a remediation caused an improvement unless
   the available telemetry supports that conclusion.

9. If the issue remains unresolved, recommend returning to the
   Diagnostician for further investigation.

10. If the issue is resolved, clearly state that no further
    diagnostic investigation is required.

11. Keep responses concise, analytical, and useful for engineers.

12. Current tool results take precedence over assumptions,
    previous context, or expected outcomes.
"""


class VerifyAgent:
    """
    Sentinel agent responsible for verifying whether
    infrastructure issues have been resolved.
    """

    def __init__(self):
        self.client = get_gemini_client()

        self.tools: List[BaseTool] = get_tools()

        logger.info(
            "Verify agent initialized with %d tools.",
            len(self.tools),
        )

    def _create_agent(self, model_name: str):
        """
        Create a LangChain verification agent using
        the specified Gemini model.
        """

        logger.info(
            "Creating verify agent with model: %s",
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

    def invoke(self, message: str) -> str:
        """
        Verify the current infrastructure state using
        the configured Gemini fallback chain.
        """

        logger.info(
            "Verification request: %s",
            message,
        )

        errors = []

        for model_name in self.client.models:
            try:
                logger.info(
                    "Trying verify agent with Gemini model: %s",
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

                logger.info(
                    "Verify agent succeeded using model: %s",
                    model_name,
                )

                return response

            except Exception as exc:
                error_message = str(exc)

                logger.warning(
                    "Verify model failed: %s | %s",
                    model_name,
                    error_message,
                )

                errors.append(
                    f"{model_name}: {error_message}"
                )

        raise RuntimeError(
            "All configured Gemini models failed for the "
            "verification agent.\n"
            + "\n".join(errors)
        )