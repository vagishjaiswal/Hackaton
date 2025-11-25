"""
Test Script for OpenAI Provider

This script demonstrates the usage of the OpenAI provider
and can be used for manual testing during development.

Run this after setting up your .env file with OPENAI_API_KEY

Author: AI Assistant
Date: 2024-12-19
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import OpenAIProvider, LLMConfig


async def test_basic_generation():
    """Test basic text generation."""
    print("=" * 60)
    print("TEST 1: Basic Text Generation")
    print("=" * 60)
    
    try:
        # Get API key from environment or .env file
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        # Create provider
        llm_config = LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100
        )
        provider = OpenAIProvider(llm_config, api_key)
        
        print(f"Provider: {provider}")
        print("\nGenerating response...\n")
        
        # Generate response
        response = await provider.generate(
            prompt="Explain what artificial intelligence is in one sentence.",
            system_prompt="You are a helpful AI assistant."
        )
        
        print(f"Response: {response}\n")
        print("✅ Test passed!\n")
        
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


async def test_conversation():
    """Test conversation with message history."""
    print("=" * 60)
    print("TEST 2: Conversation with Messages")
    print("=" * 60)
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        llm_config = LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=150
        )
        provider = OpenAIProvider(llm_config, api_key)
        
        # Create conversation
        messages = [
            {"role": "system", "content": "You are a helpful assistant that gives concise answers."},
            {"role": "user", "content": "What is Python?"}
        ]
        
        print("Messages:")
        for msg in messages:
            print(f"  {msg['role']}: {msg['content']}")
        
        print("\nGenerating response...\n")
        
        response = await provider.generate_with_messages(messages)
        
        print(f"Response: {response}\n")
        print("✅ Test passed!\n")
        
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


def test_sync_generation():
    """Test synchronous generation."""
    print("=" * 60)
    print("TEST 3: Synchronous Generation")
    print("=" * 60)
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        llm_config = LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=50
        )
        provider = OpenAIProvider(llm_config, api_key)
        
        print("Generating response synchronously...\n")
        
        response = provider.generate_sync(
            prompt="What is the capital of France?",
            system_prompt="Answer in one word."
        )
        
        print(f"Response: {response}\n")
        print("✅ Test passed!\n")
        
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


def test_streaming():
    """Test streaming generation."""
    print("=" * 60)
    print("TEST 4: Streaming Generation")
    print("=" * 60)
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        llm_config = LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.8,
            max_tokens=100
        )
        provider = OpenAIProvider(llm_config, api_key)
        
        print("Streaming response: ", end="", flush=True)
        
        for chunk in provider.stream_generate(
            prompt="Count from 1 to 5 with a sentence for each number.",
            system_prompt="Be concise."
        ):
            print(chunk, end="", flush=True)
        
        print("\n\n✅ Test passed!\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        raise


def test_config_update():
    """Test configuration updates."""
    print("=" * 60)
    print("TEST 5: Configuration Updates")
    print("=" * 60)
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        llm_config = LLMConfig(
            model="gpt-3.5-turbo",
            temperature=0.5
        )
        provider = OpenAIProvider(llm_config, api_key)
        
        print(f"Initial config: {provider.get_config()}")
        
        # Update configuration
        provider.update_config(temperature=0.9, max_tokens=50)
        
        print(f"Updated config: {provider.get_config()}")
        print("\n✅ Test passed!\n")
        
    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("OPENAI PROVIDER TEST SUITE")
    print("=" * 60 + "\n")
    
    
    
    try:
        # Run async tests
        await test_basic_generation()
        await test_conversation()
        
        # Run sync tests
        test_sync_generation()
        test_streaming()
        test_config_update()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ TEST SUITE FAILED: {e}")
        print("=" * 60 + "\n")
        raise


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_all_tests())
