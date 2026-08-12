import logging
from typing import List

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from app.genai.client import get_gemini_client
from app.tools.registry import get_tools


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are Sentinel, an infrastructure incident diagnostician.

Your job is to investigate infrastructure problems using current
server telemetry and determine the most plausible explanations.

You have access to tools that provide:

- Current server status and resource usage
- Recent system logs
- ERROR-level logs
- Log summaries
- Servers with high CPU or memory usage
- ERROR counts grouped by server and service

Your responsibility is diagnosis, not speculation.

Rules:

1. Always use the available monitoring tools before diagnosing
   an infrastructure problem.

2. Never invent servers, metrics, logs, timestamps, errors,
   services, or system behavior.

3. Base every diagnosis on evidence returned by the tools.

4. Clearly separate:

   - Observed evidence
   - Suspected cause
   - Supporting evidence
   - Contradicting evidence
   - Confidence
   - Recommended investigation

5. A correlation does not automatically establish causation.

6. Treat CPU or memory usage of 85% or higher as elevated resource
   usage.

7. Repeated ERROR logs are evidence of an error condition, but they
   do not by themselves establish the root cause.

8. When resource pressure and errors occur on different servers,
   do not claim that one caused the other without supporting evidence.

9. When multiple possible causes exist, rank the hypotheses from
   most plausible to least plausible.

10. Do not claim a definitive root cause unless the available
    telemetry provides sufficient evidence.

11. If the telemetry is insufficient to determine the cause,
    explicitly state:

    "Root cause cannot be determined from the available telemetry."

12. When useful, recommend the next specific investigation needed
    to distinguish between competing hypotheses.

13. Current telemetry always takes precedence over assumptions
    or previously observed information.

14. Keep the final diagnosis concise but useful for an engineer.

Preferred response structure:

Observed Evidence:
- ...

Likely Diagnosis:
- ...

Supporting Evidence:
- ...

Contradicting Evidence:
- ...

Confidence:
- High / Medium / Low

Recommended Investigation:
1. ...
2. ...
"""


class Diagnostician:
    """
    Sentinel agent responsible for diagnosing infrastructure problems.

    The diagnostician uses current monitoring telemetry to generate
    evidence-based hypotheses and recommend further investigation.
    """

    def __init__(self):
        self.client = get_gemini_client()

        self.tools: List[BaseTool] = get_tools()

        logger.info(
            "Diagnostician initialized with %d tools.",
            len(self.tools),
        )

    def _create_agent(self, model_name: str):
        """
        Create a LangChain diagnostic agent using the specified
        Gemini model.
        """

        logger.info(
            "Creating diagnostician with model: %s",
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
            raise RuntimeError(
                "Diagnostician returned no messages."
            )

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
                    text_parts.append(
                        part.get("text", "")
                    )

            return "".join(text_parts)

        return str(content)

    def invoke(self, message: str) -> str:
        """
        Diagnose an infrastructure problem using current telemetry.

        Configured Gemini models are attempted in order until one
        successfully completes the diagnosis.
        """

        logger.info(
            "Diagnostic request: %s",
            message,
        )

        errors = []

        for model_name in self.client.models:
            try:
                logger.info(
                    "Trying diagnostician with Gemini model: %s",
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
                    "Diagnostician succeeded using model: %s",
                    model_name,
                )

                return response

            except Exception as exc:
                error_message = str(exc)

                logger.warning(
                    "Diagnostician model failed: %s | %s",
                    model_name,
                    error_message,
                )

                errors.append(
                    f"{model_name}: {error_message}"
                )

        raise RuntimeError(
            "All configured Gemini models failed for the "
            "diagnostician.\n"
            + "\n".join(errors)
        )