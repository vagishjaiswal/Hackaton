"""
Ollama LLM Provider Implementation

This module implements the Ollama provider for local LLM interactions.
Ollama allows running models like Llama 2, Mistral, CodeLlama locally.

Features:
- Run models locally without API costs
- Privacy-focused (no data sent to external servers)
- Support for various open-source models
- Same interface as OpenAI provider

Installation:
    1. Install Ollama: https://ollama.ai
    2. Pull a model: ollama pull llama2
    3. Start Ollama service (usually automatic)

Author: AI Assistant
Date: 2024-11-26
"""

import asyncio
import logging
import requests
from typing import Any, Dict, List, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from .base_llm_provider import BaseLLMProvider, LLMConfig


# Configure logging
logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama LLM Provider implementation for local models.
    
    This provider enables running open-source LLMs locally without API costs.
    Perfect for development, testing, and privacy-sensitive applications.
    
    Supported Models (examples):
        - llama2 (7B, 13B, 70B)
        - mistral (7B)
        - codellama (7B, 13B, 34B)
        - neural-chat (7B)
        - starling-lm (7B)
        - orca-mini (3B, 7B, 13B)
        - phi (2.7B - very fast)
    
    Features:
        - No API key required
        - Run completely offline
        - Free to use
        - Privacy-focused
        - Fast inference on local hardware
    
    Example:
        ```python
        config = LLMConfig(model="llama2", temperature=0.7)
        provider = OllamaProvider(config, base_url="http://localhost:11434")
        
        # Generate response
        response = await provider.generate("What is AI?")
        ```
    """
    
    def __init__(
        self, 
        config: LLMConfig, 
        base_url: str = "http://localhost:11434",
        api_key: str = "not-needed"  # For interface compatibility
    ):
        """
        Initialize the Ollama provider.
        
        Args:
            config: LLM configuration object
            base_url: Ollama server URL (default: http://localhost:11434)
            api_key: Not needed for Ollama, kept for interface compatibility
            
        Raises:
            ConnectionError: If cannot connect to Ollama service
        """
        # Pass dummy API key to satisfy parent class
        super().__init__("ollama", config, api_key)
        self.base_url = base_url
        self._verify_ollama_running()
        self._client = self._initialize_client()
        logger.info(f"Initialized Ollama provider with model: {config.model}")
    
    def _verify_ollama_running(self) -> None:
        """
        Verify that Ollama service is running and accessible.
        
        Raises:
            ConnectionError: If Ollama is not accessible
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            # Check if model is available
            available_models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in available_models]
            
            if not any(self.config.model in name for name in model_names):
                logger.warning(
                    f"Model '{self.config.model}' not found. "
                    f"Available models: {model_names}. "
                    f"Run: ollama pull {self.config.model}"
                )
            
        except requests.exceptions.RequestException as e:
            error_msg = (
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Please ensure Ollama is installed and running.\n"
                f"Installation: https://ollama.ai\n"
                f"Error: {e}"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    def _initialize_client(self) -> ChatOllama:
        """
        Initialize the Ollama client using LangChain.
        
        Returns:
            Configured ChatOllama instance
        """
        try:
            client = ChatOllama(
                model=self.config.model,
                temperature=self.config.temperature,
                base_url=self.base_url,
                timeout=self.config.timeout,
            )
            
            # Set additional parameters if provided
            if self.config.top_p is not None:
                client.top_p = self.config.top_p
            
            return client
        
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
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
        Generate a response from Ollama asynchronously.
        
        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            **kwargs: Additional Ollama-specific parameters
            
        Returns:
            The generated text response
            
        Example:
            ```python
            response = await provider.generate(
                "Explain machine learning",
                system_prompt="You are a helpful AI tutor"
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
            logger.debug(f"Generating response with Ollama for: {prompt[:50]}...")
            response = await self._client.ainvoke(messages, **kwargs)
            
            logger.debug("Response generated successfully")
            return response.content
        
        except Exception as e:
            logger.error(f"Error generating response with Ollama: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
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
            **kwargs: Additional Ollama-specific parameters
            
        Returns:
            The generated text response
            
        Example:
            ```python
            messages = [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "What is Python?"}
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
        
        Args:
            prompt: The user prompt/query
            system_prompt: Optional system prompt for context
            **kwargs: Additional parameters
            
        Returns:
            The generated text response
            
        Example:
            ```python
            response = provider.generate_sync("What is AI?")
            ```
        """
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Generate response synchronously
            response = self._client.invoke(messages, **kwargs)
            
            return response.content
        
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
        Stream tokens as they're generated.
        
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
    
    def list_available_models(self) -> List[str]:
        """
        List all models available in local Ollama installation.
        
        Returns:
            List of model names
            
        Example:
            ```python
            models = provider.list_available_models()
            print(f"Available models: {models}")
            ```
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [m.get("name", "") for m in models]
        
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """
        Download a model from Ollama registry.
        
        Args:
            model_name: Name of model to download (e.g., "llama2")
            
        Returns:
            True if successful, False otherwise
            
        Example:
            ```python
            success = provider.pull_model("llama2")
            if success:
                print("Model downloaded successfully")
            ```
        """
        try:
            logger.info(f"Pulling model: {model_name}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minutes for download
            )
            response.raise_for_status()
            logger.info(f"Model {model_name} pulled successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model details (size, parameters, etc.)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.config.model},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}
    
    def validate_model(self) -> bool:
        """
        Validate that the configured model is available.
        
        Returns:
            True if model is available, False otherwise
        """
        available_models = self.list_available_models()
        is_valid = any(
            self.config.model in model 
            for model in available_models
        )
        
        if not is_valid:
            logger.warning(
                f"Model '{self.config.model}' not found. "
                f"Available models: {available_models}. "
                f"Run: ollama pull {self.config.model}"
            )
        
        return is_valid
    
    def estimate_speed(self) -> str:
        """
        Estimate generation speed based on model size.
        
        Returns:
            Speed estimate as string
        """
        model_name = self.config.model.lower()
        
        if "3b" in model_name or "phi" in model_name:
            return "Very Fast (~50-100 tokens/sec)"
        elif "7b" in model_name:
            return "Fast (~20-50 tokens/sec)"
        elif "13b" in model_name:
            return "Moderate (~10-20 tokens/sec)"
        elif "34b" in model_name or "70b" in model_name:
            return "Slow (~5-10 tokens/sec)"
        else:
            return "Unknown (depends on hardware)"
