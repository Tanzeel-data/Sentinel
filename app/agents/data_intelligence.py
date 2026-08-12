import logging
from typing import List

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from app.genai.client import get_gemini_client
from app.tools.registry import get_tools

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are Sentinel, an AI data intelligence agent.

Your job is to analyze infrastructure telemetry and transform raw
monitoring data into useful operational insights.

You have access to tools that provide:

- Current server status and resource usage
- Recent system logs
- ERROR-level logs
- Log summaries
- Servers with high CPU or memory usage
- ERROR counts grouped by server and service

Rules:

1. Always use the appropriate monitoring tools when the user asks
   about actual infrastructure data.

2. Never invent servers, metrics, logs, counts, timestamps, or trends.

3. Base conclusions only on observed telemetry.

4. Clearly distinguish:
   - Observed data
   - Patterns or trends
   - Potential significance
   - Recommended next investigation

5. When comparing servers, services, or metrics, use the actual
   telemetry returned by the tools.

6. Do not claim causation unless the available telemetry supports it.

7. If the available data is insufficient to establish a pattern,
   explicitly say so.

8. Keep responses concise, analytical, and useful for engineers.

9. When multiple findings exist, prioritize the most significant
   finding first.

10. Do not treat assumptions or previous context as current telemetry.
    Current tool results take precedence.
"""


class DataIntelligenceAgent:
    """
    Sentinel agent responsible for extracting operational insights
    from infrastructure telemetry.

    The agent uses the centralized Gemini configuration and attempts
    configured Gemini models in order when a model fails.
    """

    def __init__(self):
        self.client = get_gemini_client()

        self.tools: List[BaseTool] = get_tools()

        logger.info(
            "Data intelligence agent initialized with %d tools.",
            len(self.tools),
        )

    def _create_agent(self, model_name: str):
        """
        Create a LangChain agent using the specified Gemini model.
        """

        logger.info(
            "Creating data intelligence agent with model: %s",
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
        Process a data intelligence request using the configured
        Gemini fallback chain.
        """

        logger.info(
            "Data intelligence request: %s",
            message,
        )

        errors = []

        for model_name in self.client.models:
            try:
                logger.info(
                    "Trying data intelligence agent with Gemini model: %s",
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
                    "Data intelligence agent succeeded using model: %s",
                    model_name,
                )

                return response

            except Exception as exc:
                error_message = str(exc)

                logger.warning(
                    "Data intelligence model failed: %s | %s",
                    model_name,
                    error_message,
                )

                errors.append(
                    f"{model_name}: {error_message}"
                )

        raise RuntimeError(
            "All configured Gemini models failed for the "
            "data intelligence agent.\n"
            + "\n".join(errors)
        )