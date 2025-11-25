"""
LLM Provider Factory

Factory pattern for creating LLM providers dynamically.
Supports both cloud-based (OpenAI, Gemini) and local (Ollama) providers.
"""

from enum import Enum
from typing import Optional
from .base_llm_provider import LLMConfig, BaseLLMProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"  # Coming soon


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create(
        provider_type: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_type: Type of provider ("openai", "ollama", "gemini")
            model: Model name/identifier
            api_key: API key (required for cloud providers)
            base_url: Base URL for local providers (e.g., Ollama)
            **kwargs: Additional provider-specific parameters

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider type is not supported
        """
        config = LLMConfig(model=model, **kwargs)

        if provider_type == ProviderType.OPENAI:
            if not api_key:
                raise ValueError("api_key required for OpenAI provider")
            return OpenAIProvider(config, api_key)

        elif provider_type == ProviderType.OLLAMA:
            return OllamaProvider(config, base_url=base_url)

        elif provider_type == ProviderType.GEMINI:
            raise NotImplementedError("Gemini provider coming soon")

        else:
            raise ValueError(
                f"Unsupported provider type: {provider_type}. "
                f"Supported: {[p.value for p in ProviderType]}"
            )


def create_llm_provider(
    provider_type: str,
    model: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseLLMProvider:
    """
    Convenience function to create an LLM provider.

    Example:
        provider = create_llm_provider("openai", "gpt-4", api_key="sk-...")
        provider = create_llm_provider("ollama", "llama2")
    """
    return LLMProviderFactory.create(provider_type, model, api_key, base_url, **kwargs)
