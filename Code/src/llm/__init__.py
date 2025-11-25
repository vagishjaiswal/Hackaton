"""
LLM Module - Language Model Provider Implementations

This module provides abstractions and implementations for various LLM providers.
Currently supports:
- OpenAI (GPT-4, GPT-3.5) - Cloud API
- Ollama (Llama2, Mistral, etc.) - Local models
- Google Gemini (coming soon)

Usage:
    # OpenAI (cloud)
    from src.llm import OpenAIProvider, LLMConfig
    config = LLMConfig(model="gpt-4", temperature=0.7)
    provider = OpenAIProvider(config, api_key="your-key")
    
    # Ollama (local)
    from src.llm import OllamaProvider, LLMConfig
    config = LLMConfig(model="llama2", temperature=0.7)
    provider = OllamaProvider(config)
    
    # Factory pattern (recommended)
    from src.llm import create_llm_provider
    provider = create_llm_provider("ollama", "llama2")
    
    # Generate response
    response = await provider.generate("Hello!")

Author: AI Assistant
Date: 2024-11-26
"""

from .base_llm_provider import BaseLLMProvider, LLMConfig
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .llm_provider_factory import (
    LLMProviderFactory,
    ProviderType,
    create_llm_provider
)

__all__ = [
    "BaseLLMProvider",
    "LLMConfig",
    "OpenAIProvider",
    "OllamaProvider",
    "LLMProviderFactory",
    "ProviderType",
    "create_llm_provider",
]

__version__ = "0.2.0"
