import logging
from typing import List

from langchain.agents import create_agent
from langchain_core.tools import BaseTool

from app.genai.client import get_gemini_client
from app.tools.registry import get_tools


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are Sentinel, an AI infrastructure monitoring assistant.

Your job is to help users understand system telemetry, server health,
and application logs.

You have access to monitoring tools. Use them when the user's question
requires actual telemetry data.

Rules:

1. Never invent server, log, CPU, memory, or incident information.

2. Use the appropriate monitoring tool before answering telemetry questions.

3. If the user asks about server health, inspect server status and
   resource usage.

4. If the user asks about recent activity, inspect recent logs.

5. If the user asks about errors or failures, inspect error logs.

6. If the user asks for log statistics or severity counts, inspect
   the log summary.

7. Clearly distinguish observed telemetry from your interpretation.

8. Keep responses concise and operationally useful.

9. If the available telemetry does not contain enough information to
   answer, say so explicitly.
"""


class MonitoringAgent:
    """
    Gemini-powered Sentinel monitoring agent.

    Uses the centralized Gemini model configuration and automatically
    falls back to the next configured Gemini model if the current
    model fails.
    """

    def __init__(self):
        self.client = get_gemini_client()

        self.tools: List[BaseTool] = get_tools()

        logger.info(
            "Monitoring agent initialized with %d tools.",
            len(self.tools),
        )

    def _create_agent(self, model_name: str):
        """
        Create a LangChain agent using the specified Gemini model.
        """

        logger.info(
            "Creating monitoring agent with model: %s",
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
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))

            return "".join(text_parts)

        return str(content)

    def invoke(self, message: str) -> str:
        """
        Process a monitoring request using the configured Gemini
        fallback chain.

        Models are attempted in the order defined by GEMINI_MODELS.
        """

        logger.info(
            "Monitoring request: %s",
            message,
        )

        errors = []

        for model_name in self.client.models:
            try:
                logger.info(
                    "Trying monitoring agent with Gemini model: %s",
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
                    "Monitoring agent succeeded using model: %s",
                    model_name,
                )

                return response

            except Exception as exc:
                error_message = str(exc)

                logger.warning(
                    "Monitoring agent model failed: %s | %s",
                    model_name,
                    error_message,
                )

                errors.append(
                    f"{model_name}: {error_message}"
                )

        raise RuntimeError(
            "All configured Gemini models failed for the monitoring agent.\n"
            + "\n".join(errors)
        )