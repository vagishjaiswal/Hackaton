"""
Base LLM Provider Abstract Class

This module defines the abstract base class for all LLM providers.
All concrete provider implementations (OpenAI, Gemini, etc.) must inherit from this class.

Author: AI Assistant
Date: 2024-12-19
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration model for LLM providers."""
    
    model: str = Field(..., description="Model name/identifier")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens in response")
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0, description="Presence penalty")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    
    class Config:
        extra = "allow"  # Allow additional provider-specific fields


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This class defines the interface that all LLM providers must implement.
    It handles common functionality like configuration validation, error handling,
    and retry logic patterns.
    
    Attributes:
        provider_name (str): Name of the provider (e.g., "openai", "gemini")
        config (LLMConfig): Configuration for the LLM
        api_key (str): API key for authentication
    """
    
    def __init__(self, provider_name: str, config: LLMConfig, api_key: str):
        """
        Initialize the LLM provider.
        
        Args:
            provider_name: Name identifier for this provider
            config: Configuration object for the LLM
            api_key: API key for authentication
            
        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key or not api_key.strip():
            raise ValueError(f"{provider_name} API key cannot be empty")
        
        self.provider_name = provider_name
        self.config = config
        self.api_key = api_key
        self._client = None  # Will be initialized by concrete classes
        
    @abstractmethod
    def _initialize_client(self) -> Any:
        """
        Initialize the provider-specific client.
        
        This method must be implemented by each concrete provider class
        to set up their specific client library.
        
        Returns:
            The initialized client object
        """
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated text response
            
        Raises:
            Exception: If generation fails after all retries
        """
        pass
    
    @abstractmethod
    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a response from a list of messages (chat format).
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "user", "content": "Hello"}]
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated text response
            
        Raises:
            Exception: If generation fails after all retries
        """
        pass
    
    @abstractmethod
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Synchronous version of generate method.
        
        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated text response
        """
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration as a dictionary.
        
        Returns:
            Dictionary containing all configuration parameters
        """
        return self.config.model_dump()
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Example:
            provider.update_config(temperature=0.5, max_tokens=1000)
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def __repr__(self) -> str:
        """String representation of the provider."""
        return (
            f"{self.__class__.__name__}("
            f"provider={self.provider_name}, "
            f"model={self.config.model}, "
            f"temperature={self.config.temperature})"
        )
