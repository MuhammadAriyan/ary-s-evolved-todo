"""AI client configuration for OpenAI Agents SDK.

This module configures the AI client with custom provider support.
Call initialize_ai_client() at application startup.
"""
from openai import AsyncOpenAI
from agents import set_default_openai_client, OpenAIChatCompletionsModel

from app.config import settings


_ai_client: AsyncOpenAI | None = None
_ai_model: OpenAIChatCompletionsModel | None = None


def get_ai_client() -> AsyncOpenAI:
    """Get the configured AI client instance.

    Returns:
        AsyncOpenAI: The configured AI client

    Raises:
        RuntimeError: If AI client not initialized
    """
    if _ai_client is None:
        raise RuntimeError(
            "AI client not initialized. Call initialize_ai_client() at startup."
        )
    return _ai_client


def initialize_ai_client() -> None:
    """Initialize the AI client with configuration from environment.

    Must be called at application startup before using any agents.
    Uses AI_API_KEY, AI_BASE_URL, and AI_MODEL from environment.
    """
    global _ai_client, _ai_model

    if not settings.ai_api_key:
        raise ValueError(
            "AI_API_KEY environment variable is required for AI chatbot functionality"
        )

    # Create custom OpenAI client with configured provider (e.g., OpenRouter)
    _ai_client = AsyncOpenAI(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url,
    )

    # Create OpenAIChatCompletionsModel for non-OpenAI providers
    _ai_model = OpenAIChatCompletionsModel(
        model=settings.ai_model,
        openai_client=_ai_client,
    )

    # Set as default for all agents in the SDK
    set_default_openai_client(_ai_client)


def get_ai_model() -> OpenAIChatCompletionsModel:
    """Get the configured AI model.

    Returns:
        OpenAIChatCompletionsModel: The configured model for use with agents
    """
    if _ai_model is None:
        raise RuntimeError(
            "AI model not initialized. Call initialize_ai_client() at startup."
        )
    return _ai_model


def get_ai_model_name() -> str:
    """Get the configured AI model name.

    Returns:
        str: The model name (e.g., 'nvidia/nemotron-3-nano-30b-a3b:free')
    """
    return settings.ai_model


def is_ai_configured() -> bool:
    """Check if AI client is properly configured.

    Returns:
        bool: True if AI_API_KEY is set
    """
    return bool(settings.ai_api_key)
