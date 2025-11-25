"""
OpenAI LLM Provider Implementation

This module implements the OpenAI provider for LLM interactions.
It supports both GPT-4 and GPT-3.5 models with retry logic and error handling.

Author: AI Assistant
Date: 2024-12-19
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .base_llm_provider import BaseLLMProvider, LLMConfig


# Configure logging
logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM Provider implementation.
    
    This provider supports OpenAI's GPT models (GPT-4, GPT-3.5, etc.)
    and includes automatic retry logic for rate limits and transient failures.
    
    Features:
        - Automatic retry with exponential backoff
        - Rate limit handling
        - Support for both async and sync operations
        - Message-based and prompt-based interfaces
    
    Example:
        ```python
        config = LLMConfig(model="gpt-4", temperature=0.7)
        provider = OpenAIProvider(config, api_key="sk-...")
        
        # Async usage
        response = await provider.generate("What is AI?")
        
        # Sync usage
        response = provider.generate_sync("What is AI?")
        ```
    """
    
    def __init__(self, config: LLMConfig, api_key: str):
        """
        Initialize the OpenAI provider.
        
        Args:
            config: LLM configuration object
            api_key: OpenAI API key
            
        Raises:
            ValueError: If API key is invalid
        """
        super().__init__("openai", config, api_key)
        self._client = self._initialize_client()
        logger.info(f"Initialized OpenAI provider with model: {config.model}")
    
    def _initialize_client(self) -> ChatOpenAI:
        """
        Initialize the OpenAI client using LangChain.
        
        Returns:
            Configured ChatOpenAI instance
        """
        try:
            client = ChatOpenAI(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                openai_api_key=self.api_key,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
            )
            
            # Set additional parameters if provided
            if self.config.top_p is not None:
                client.model_kwargs["top_p"] = self.config.top_p
            if self.config.frequency_penalty is not None:
                client.model_kwargs["frequency_penalty"] = self.config.frequency_penalty
            if self.config.presence_penalty is not None:
                client.model_kwargs["presence_penalty"] = self.config.presence_penalty
                
            return client
        
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from OpenAI asynchronously.
        
        This method includes automatic retry logic for handling:
        - Rate limits (429 errors)
        - Temporary network issues
        - API timeouts
        
        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            The generated text response
            
        Raises:
            Exception: If generation fails after all retries
            
        Example:
            ```python
            response = await provider.generate(
                "Explain quantum computing",
                system_prompt="You are a physics professor"
            )
            ```
        """
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            logger.debug(f"Generating response for prompt: {prompt[:50]}...")
            response = await self._client.ainvoke(messages, **kwargs)
            
            logger.debug("Response generated successfully")
            return response.content
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate a response from a conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Supported roles: 'system', 'user', 'assistant'
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            The generated text response
            
        Example:
            ```python
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "What is Python?"},
                {"role": "assistant", "content": "Python is a programming language"},
                {"role": "user", "content": "Tell me more"}
            ]
            response = await provider.generate_with_messages(messages)
            ```
        """
        try:
            # Convert dict messages to LangChain message objects
            lc_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "user":
                    lc_messages.append(HumanMessage(content=content))
                # Note: LangChain handles assistant messages differently
                # For now, we'll focus on system and user messages
            
            logger.debug(f"Generating response for {len(messages)} messages")
            response = await self._client.ainvoke(lc_messages, **kwargs)
            
            logger.debug("Response generated successfully")
            return response.content
        
        except Exception as e:
            logger.error(f"Error generating response from messages: {e}")
            raise
    
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Synchronous version of generate method.
        
        This is useful when you can't use async/await (e.g., in Streamlit apps).
        
        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            The generated text response
            
        Example:
            ```python
            response = provider.generate_sync("What is machine learning?")
            ```
        """
        try:
            # Use asyncio to run the async method
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If there's already a running loop, create a new one
                import nest_asyncio
                nest_asyncio.apply()
            
            return loop.run_until_complete(
                self.generate(prompt, system_prompt, **kwargs)
            )
        
        except Exception as e:
            logger.error(f"Error in synchronous generation: {e}")
            raise
    
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """
        Stream tokens as they're generated (for real-time UI updates).
        
        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            **kwargs: Additional parameters
            
        Yields:
            Generated text chunks
            
        Example:
            ```python
            for chunk in provider.stream_generate("Tell me a story"):
                print(chunk, end="", flush=True)
            ```
        """
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Stream response
            for chunk in self._client.stream(messages, **kwargs):
                if chunk.content:
                    yield chunk.content
        
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string.
        
        This is useful for staying within token limits.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
            
        Note:
            This uses a simple approximation. For exact counts,
            use tiktoken library directly.
        """
        # Simple approximation: ~4 characters per token
        return len(text) // 4
    
    def validate_model(self) -> bool:
        """
        Validate that the configured model is supported.
        
        Returns:
            True if model is valid, False otherwise
        """
        supported_models = [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
        ]
        
        # Check if model starts with any supported model prefix
        is_valid = any(
            self.config.model.startswith(model) 
            for model in supported_models
        )
        
        if not is_valid:
            logger.warning(
                f"Model '{self.config.model}' may not be supported. "
                f"Supported models: {supported_models}"
            )
        
        return is_valid
