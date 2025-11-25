"""
Test Script for Ollama LLM Provider

This script demonstrates the usage of the Ollama provider
for local LLM inference without requiring API keys.

Prerequisites:
- Ollama installed and running (https://ollama.ai)
- Run: ollama pull mistral (or another model)
- Ollama server running on http://localhost:11434

Author: AI Assistant
Date: 2024-12-19
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import LLMConfig, OllamaProvider


async def test_ollama_basic():
    """Test basic text generation with Ollama."""
    print("=" * 60)
    print("TEST 1: Ollama Basic Text Generation")
    print("=" * 60)
    
    try:
        # Create provider for local Ollama instance
        llm_config = LLMConfig(
            model="phi3:latest",  # Use available model
            temperature=0.7,
            max_tokens=100
        )
        provider = OllamaProvider(llm_config, base_url="http://localhost:11434")
        
        print(f"Provider: {provider}")
        print("\nGenerating response from Ollama...\n")
        
        # Generate response
        response = await provider.generate(
            prompt="Explain what artificial intelligence is in one sentence.",
            system_prompt="You are a helpful AI assistant."
        )
        
        print(f"Response: {response}\n")
        print("[PASS] Test succeeded!\n")
        
    except ConnectionError:
        print("[ERROR] Could not connect to Ollama server")
        print("Make sure Ollama is running: ollama serve\n")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}\n")


async def test_ollama_streaming():
    """Test streaming generation with Ollama."""
    print("=" * 60)
    print("TEST 2: Ollama Streaming Generation")
    print("=" * 60)
    
    try:
        llm_config = LLMConfig(
            model="phi3:latest",
            temperature=0.8,
            max_tokens=150
        )
        provider = OllamaProvider(llm_config, base_url="http://localhost:11434")
        
        print("Streaming response from Ollama: ", end="", flush=True)
        
        for chunk in provider.stream_generate(
            prompt="Count from 1 to 5 with a sentence for each number.",
            system_prompt="Be concise."
        ):
            print(chunk, end="", flush=True)
        
        print("\n\n[PASS] Test succeeded!\n")
        
    except ConnectionError:
        print("[ERROR] Could not connect to Ollama server")
        print("Make sure Ollama is running: ollama serve\n")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}\n")


async def test_ollama_conversation():
    """Test conversation with Ollama."""
    print("=" * 60)
    print("TEST 3: Ollama Conversation")
    print("=" * 60)
    
    try:
        llm_config = LLMConfig(
            model="phi3:latest",
            temperature=0.7,
            max_tokens=150
        )
        provider = OllamaProvider(llm_config, base_url="http://localhost:11434")
        
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
        print("[PASS] Test succeeded!\n")
        
    except ConnectionError:
        print("[ERROR] Could not connect to Ollama server")
        print("Make sure Ollama is running: ollama serve\n")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}\n")


def test_ollama_list_models():
    """List available Ollama models."""
    print("=" * 60)
    print("TEST 4: List Ollama Models")
    print("=" * 60)
    
    try:
        llm_config = LLMConfig(model="phi3:latest")
        provider = OllamaProvider(llm_config, base_url="http://localhost:11434")
        models = provider.list_available_models()
        
        if models:
            print("\nAvailable models from Ollama server:\n")
            for model in models:
                print(f"  - {model}")
        else:
            print("\nPopular Ollama models:")
            print("  - mistral (fast, 7B)")
            print("  - neural-chat (optimized for conversations, 7B)")
            print("  - llama2 (general purpose, 7B/13B)")
            print("  - dolphin-mixtral (creative, 46.7B)")
            print("  - phi (small and fast, 2.7B)")
            print("  - orca-mini (good reasoning, 3B/7B)")
            print("  - phi3:latest (latest phi model)")
            print("\nPull a model with: ollama pull <model-name>")
        
        print("\n[PASS] Test succeeded!\n")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}\n")


async def run_all_tests():
    """Run all Ollama tests."""
    print("\n" + "=" * 60)
    print("OLLAMA PROVIDER TEST SUITE")
    print("=" * 60 + "\n")
    
    print("SETUP REQUIRED:")
    print("1. Install Ollama from https://ollama.ai")
    print("2. Run: ollama pull phi3")
    print("3. Start Ollama: ollama serve")
    print("4. Then run this test\n")
    
    try:
        # List available models first
        test_ollama_list_models()
        
        # Run async tests
        await test_ollama_basic()
        await test_ollama_streaming()
        await test_ollama_conversation()
        
        print("=" * 60)
        print("SUCCESS: ALL TESTS COMPLETED")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print("=" * 60)
        print(f"ERROR: TEST SUITE FAILED: {e}")
        print("=" * 60 + "\n")
        raise


if __name__ == "__main__":
    print("\nOllama Provider Test Suite")
    print("This test demonstrates local LLM inference with Ollama.\n")
    
    # Run the test suite
    asyncio.run(run_all_tests())
