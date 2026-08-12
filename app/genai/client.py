import logging
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Central Gemini client with ordered model fallback.

    Models are configured through the GEMINI_MODELS environment variable:

        GEMINI_MODELS=model-a,model-b,model-c
    """

    def __init__(self):
        self.models = [
            model.strip()
            for model in os.getenv("GEMINI_MODELS", "").split(",")
            if model.strip()
        ]

        if not self.models:
            raise ValueError(
                "GEMINI_MODELS is not configured in the environment."
            )

        self.api_key = os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY is not configured in the environment."
            )

    def _create_model(self, model_name: str) -> ChatGoogleGenerativeAI:
        """Create a configured Gemini chat model."""

        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=0,
        )

    def get_model(
        self,
        model_name: str | None = None,
    ) -> ChatGoogleGenerativeAI:
        """
        Return a configured Gemini chat model.

        If a model name is supplied, that model is returned.
        Otherwise, the first configured model is returned.
        """

        selected_model = model_name or self.models[0]

        return self._create_model(selected_model)

    def get_fallback_model(self):
        """
        Return a LangChain chat model with ordered Gemini fallback.

        The first configured model is tried first. If it fails,
        LangChain automatically attempts the next configured model.
        """

        primary_model = self._create_model(self.models[0])

        fallback_models = [
            self._create_model(model_name)
            for model_name in self.models[1:]
        ]

        if not fallback_models:
            return primary_model

        fallback_chain = primary_model.with_fallbacks(
            fallback_models
        )

        logger.info(
            "Gemini fallback chain configured: %s",
            " -> ".join(self.models),
        )

        return fallback_chain

    def _extract_text(self, response) -> str:
        """
        Extract plain text from a Gemini response.

        Handles both string content and structured content returned
        by newer versions of the Google GenAI integration.
        """

        content = response.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []

            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))

            return "".join(text_parts)

        return str(content)

    def invoke(self, prompt: str) -> str:
        """
        Invoke Gemini using the configured fallback chain.

        Models are attempted in the order defined by GEMINI_MODELS.

        Returns:
            Plain-text response from the first successful model.

        Raises:
            RuntimeError: If all configured Gemini models fail.
        """

        errors = []

        for model_name in self.models:
            try:
                logger.info(
                    "Trying Gemini model: %s",
                    model_name,
                )

                model = self._create_model(model_name)
                response = model.invoke(prompt)

                text = self._extract_text(response)

                logger.info(
                    "Gemini request succeeded using model: %s",
                    model_name,
                )

                return text

            except Exception as exc:
                error_message = str(exc)

                logger.warning(
                    "Gemini model failed: %s | %s",
                    model_name,
                    error_message,
                )

                errors.append(
                    f"{model_name}: {error_message}"
                )

        raise RuntimeError(
            "All configured Gemini models failed.\n"
            + "\n".join(errors)
        )


def get_gemini_client() -> GeminiClient:
    """Return a configured GeminiClient."""

    return GeminiClient()