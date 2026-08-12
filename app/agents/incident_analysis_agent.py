import logging

from langchain.agents import create_agent

from app.genai.client import get_gemini_client
from app.tools.registry import get_tools
from app.memory import MemoryStore


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are Sentinel, an infrastructure incident analysis agent.

Your job is to analyze monitored server telemetry and identify
potential infrastructure incidents.

You have access to tools that provide:

- Current server status and resource usage
- Recent system logs
- ERROR-level logs
- Log summaries
- Servers with high CPU or memory usage
- ERROR counts grouped by server and service

You also have access to previously discovered investigation
context provided through memory.

Rules:

1. Use the available tools to obtain current telemetry before making
   claims about the infrastructure.

2. Do not invent server information, metrics, logs, or incidents.

3. Treat CPU or memory usage of 85% or higher as elevated resource usage.

4. Treat repeated ERROR logs as evidence of an error condition,
   but do not claim a root cause unless the telemetry supports it.

5. Clearly distinguish:

   - Observed facts
   - Potential impact
   - Likely cause
   - Recommended investigation

6. When multiple problems exist, identify each separately.

7. Keep the final response concise but useful for an engineer.

8. If the available telemetry is insufficient to determine the cause,
   explicitly say that additional investigation is required.

9. When previous investigation context is provided, use it to answer
   follow-up questions.

10. Do not treat memory as a replacement for current telemetry when
    the user asks about the current state.

11. Do not claim that something is currently true solely because it
    was stored in memory previously.

12. Current telemetry always takes precedence over stored memory.
"""


class IncidentAnalysisAgent:
    """
    Sentinel agent responsible for analyzing infrastructure incidents.

    Uses:
    - Centralized Gemini configuration
    - Ordered Gemini model fallback
    - Registered monitoring tools
    - Lightweight investigation memory
    """

    def __init__(self):
        self.client = get_gemini_client()

        self.tools = get_tools()

        self.memory = MemoryStore()

        logger.info(
            "Incident analysis agent initialized with %d tools.",
            len(self.tools),
        )

    def _create_agent(self, model_name: str):
        """
        Create a LangChain incident analysis agent
        using the specified Gemini model.
        """

        logger.info(
            "Creating incident analysis agent with model: %s",
            model_name,
        )

        return create_agent(
            model=f"google_genai:{model_name}",
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    @staticmethod
    def _extract_content(message) -> str:
        """
        Extract plain text from a LangChain agent message.
        """

        content = message.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []

            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))

            return "".join(text_parts)

        return str(content)

    def _build_context(self) -> str:
        """
        Build relevant context from stored memory.
        """

        memory = self.memory.get_all()

        if not memory:
            return ""

        context_parts = [
            "Previously discovered Sentinel investigation context:"
        ]

        for key, value in memory.items():
            context_parts.append(
                f"{key}: {value}"
            )

        context_parts.append(
            "Use this context only when relevant. "
            "Current telemetry takes precedence."
        )

        return "\n".join(context_parts)

    def _store_analysis_context(
        self,
        query: str,
        analysis: str,
    ) -> None:
        """
        Store the latest investigation context.
        """

        self.memory.set(
            "last_query",
            query,
        )

        self.memory.set(
            "last_analysis",
            analysis,
        )

    def _invoke_agent(
        self,
        agent,
        content: str,
    ) -> str:
        """
        Invoke a LangChain agent and extract its final response.
        """

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": content,
                    }
                ]
            }
        )

        messages = result.get("messages", [])

        if not messages:
            raise RuntimeError(
                "Incident analysis agent returned no messages."
            )

        return self._extract_content(messages[-1])

    def invoke(self, query: str) -> str:
        """
        Analyze an infrastructure incident using the configured
        Gemini fallback chain.

        Models are attempted in the order defined by GEMINI_MODELS.
        Previous investigation context is included when available.
        """

        logger.info(
            "Incident analysis request: %s",
            query,
        )

        context = self._build_context()

        user_content = query

        if context:
            user_content = (
                f"{query}\n\n"
                f"{context}"
            )

        errors = []

        for model_name in self.client.models:
            try:
                logger.info(
                    "Trying incident analysis with Gemini model: %s",
                    model_name,
                )

                agent = self._create_agent(model_name)

                analysis = self._invoke_agent(
                    agent,
                    user_content,
                )

                logger.info(
                    "Incident analysis succeeded using model: %s",
                    model_name,
                )

                self._store_analysis_context(
                    query=query,
                    analysis=analysis,
                )

                return analysis

            except Exception as exc:
                error_message = str(exc)

                logger.warning(
                    "Incident analysis model failed: %s | %s",
                    model_name,
                    error_message,
                )

                errors.append(
                    f"{model_name}: {error_message}"
                )

        raise RuntimeError(
            "All configured Gemini models failed for the "
            "incident analysis agent.\n"
            + "\n".join(errors)
        )