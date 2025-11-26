"""
Agent Examples and Demonstrations

This script demonstrates how to use different agents with both Ollama and OpenAI providers.

Features:
- Simple executor agent for general tasks
- Data analyst agent for CSV analysis
- Researcher agent for information gathering
- Both async and sync examples
- Multiple LLM provider examples

Usage:
    python examples_agent_usage.py
    
Or import in your own code:
    from examples_agent_usage import demonstrate_simple_agent
    demonstrate_simple_agent()

Author: AI Assistant
Date: 2024-11-27
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Optional

# Add src to path - adjust for tests/workflow subdirectory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents import (
    SimpleExecutorAgent,
    SyncExecutorAgent,
    DataAnalystAgent,
    ResearcherAgent,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Simple Agent with Ollama (Local)
# ============================================================================

async def example_simple_agent_ollama():
    """
    Example: Simple agent using Ollama (local LLM).
    
    Ollama is free and runs locally, perfect for development.
    Requires: Ollama installed and running (ollama serve)
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Agent with Ollama (Local)")
    print("="*70)
    
    try:
        # Create agent
        agent = SimpleExecutorAgent(
            system_prompt="You are a helpful AI assistant. Be concise and clear.",
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"[OK] Created agent: {agent}")
        
        # Execute some tasks
        tasks = [
            "What are the top 3 benefits of Python?",
            "Explain machine learning in one sentence",
            "List 5 tips for better sleep"
        ]
        
        for task in tasks:
            print(f"\n[TASK] Task: {task}")
            result = await agent.execute(task)
            print(f"[RESPONSE] Response:\n{result[:200]}...")
        
        # Show agent state
        print(f"\n[ANALYSIS] Agent Statistics:")
        print(f"  - Executions: {agent.state.execution_count}")
        print(f"  - Messages: {len(agent.state.messages)}")
        print(f"  - Tools: {agent.list_tools()}")
        
    except (ConnectionError, Exception) as e:
        print(f"[ERROR] Error: {e}")
        print("\nTo use Ollama:")
        print("  1. Install from https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. In another terminal: ollama pull llama3.2")


# ============================================================================
# Example 2: Simple Agent with OpenAI (Cloud)
# ============================================================================

async def example_simple_agent_openai():
    """
    Example: Simple agent using OpenAI (GPT-4/3.5).
    
    Requires: OPENAI_API_KEY environment variable set
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Simple Agent with OpenAI (Cloud)")
    print("="*70)
    
    try:
        # Create agent
        agent = SimpleExecutorAgent(
            system_prompt="You are a creative writing expert.",
            llm_provider="openai",
            llm_model="gpt-3.5-turbo"
        )
        print(f"[OK] Created agent: {agent}")
        
        # Execute a task
        task = "Write a short 3-sentence story about a robot learning to dance"
        print(f"\n📋 Task: {task}")
        result = await agent.execute(task)
        print(f"📝 Response:\n{result}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print("\nTo use OpenAI:")
        print("  1. Get API key from https://platform.openai.com/api-keys")
        print("  2. Set environment variable: OPENAI_API_KEY=sk-...")


# ============================================================================
# Example 3: Multi-turn Conversation
# ============================================================================

async def example_multi_turn_conversation():
    """
    Example: Multi-turn conversation with agent.
    
    Shows how agents maintain conversation history.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Multi-turn Conversation")
    print("="*70)
    
    try:
        agent = SimpleExecutorAgent(
            system_prompt="You are a helpful math tutor.",
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"[OK] Created agent: {agent.name}\n")
        
        # Multi-turn conversation
        conversation = [
            "What is a quadratic equation?",
            "Can you give me an example?",
            "How do you solve it?",
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"\n[Turn {i}] You: {message}")
            try:
                response = await agent.execute(message)
                print(f"[Turn {i}] Assistant: {response[:150]}...")
            except Exception as e:
                print(f"[Turn {i}] ERROR: {str(e)[:100]}")
                break
        
        # Show history
        print(f"\n[HISTORY] Conversation History ({len(agent.get_history())} messages):")
        for msg in agent.get_history()[-5:]:
            print(f"  {msg['role']}: {msg['content'][:50]}...")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")


# ============================================================================
# Example 4: Data Analyst Agent
# ============================================================================

async def example_data_analyst():
    """
    Example: Data analyst agent for CSV analysis.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Data Analyst Agent")
    print("="*70)
    
    try:
        # Check for CSV file - support both naming conventions
        import os
        csv_file = "data/input/sample_data.csv"
        if not os.path.exists(csv_file):
            csv_file = "data/input/sample-csv.csv"
        
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found")
        
        # Create agent
        agent = DataAnalystAgent(
            csv_file=csv_file,
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"[OK] Created agent: {agent}\n")
        
        # Analysis tasks
        tasks = [
            "What are the unique categories in this data?",
            "What is the average value across all items?",
            "Which item has the highest value?",
        ]
        
        for task in tasks:
            print(f"\n[ANALYSIS] Analysis: {task}")
            try:
                result = await agent.execute(task)
                print(f"Result: {result[:150]}...")
            except Exception as e:
                print(f"Result ERROR: {str(e)[:100]}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")


# ============================================================================
# Example 5: Researcher Agent
# ============================================================================

async def example_researcher():
    """
    Example: Researcher agent for research tasks.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Researcher Agent")
    print("="*70)
    
    try:
        agent = ResearcherAgent(
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"[OK] Created agent: {agent}\n")
        
        # Research tasks
        tasks = [
            "What are the latest trends in artificial intelligence?",
            "Explain blockchain technology",
            "What are quantum computers?",
        ]
        
        for task in tasks:
            print(f"\n[RESEARCH] Research: {task}")
            try:
                result = await agent.execute(task)
                print(f"Result: {result[:150]}...")
            except Exception as e:
                print(f"Result ERROR: {str(e)[:100]}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")


# ============================================================================
# Example 6: Synchronous Agent (for Streamlit, etc.)
# ============================================================================

def example_sync_agent():
    """
    Example: Synchronous agent (good for Streamlit, Flask, etc.).
    
    Useful when you can't use async/await.
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Synchronous Agent")
    print("="*70)
    
    try:
        agent = SyncExecutorAgent(
            system_prompt="You are a technical support expert.",
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"[OK] Created agent: {agent}\n")
        
        # Synchronous execution
        tasks = [
            "How do I fix a broken laptop screen?",
            "What are common error codes?",
        ]
        
        for task in tasks:
            print(f"\n[SUPPORT] Support: {task}")
            try:
                result = agent.execute_sync(task)
                print(f"Result: {result[:150]}...")
            except Exception as e:
                print(f"Result ERROR: {str(e)[:100]}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")


# ============================================================================
# Example 7: Agent with Context
# ============================================================================

async def example_agent_with_context():
    """
    Example: Agent with shared context.
    
    Demonstrates how to share state/context across executions.
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Agent with Context")
    print("="*70)
    
    try:
        agent = SimpleExecutorAgent(
            system_prompt="You are a project manager assistant.",
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"[OK] Created agent: {agent}\n")
        
        # Set context
        context = {
            "project": "AI Hackathon",
            "deadline": "2024-12-31",
            "team_size": 5,
            "budget": "$10,000"
        }
        agent.set_context(context)
        print(f"[CONTEXT] Context set: {context}\n")
        
        # Execute with context
        task = "What should be our milestones for the project?"
        print(f"[TASK] Task: {task}")
        try:
            result = await agent.execute(task)
            print(f"[RESPONSE] Result: {result[:150]}...\n")
        except Exception as e:
            print(f"[ERROR] Result ERROR: {str(e)[:100]}\n")
        
        # Retrieve context
        print(f"Project from context: {agent.get_context('project')}")
        print(f"All context keys: {list(agent.get_context().keys())}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")


# ============================================================================
# Example 8: Agent State Management
# ============================================================================

async def example_state_management():
    """
    Example: Agent state management and reset.
    """
    print("\n" + "="*70)
    print("EXAMPLE 8: State Management")
    print("="*70)
    
    try:
        agent = SimpleExecutorAgent(
            system_prompt="You are a helpful assistant.",
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"[OK] Created agent: {agent}\n")
        
        # Execute some tasks
        print("Executing multiple tasks...")
        for i in range(3):
            try:
                await agent.execute(f"Task {i+1}: Say 'Hello'")
            except Exception as e:
                print(f"[SKIP] Task {i+1} failed: {str(e)[:50]}")
        
        # Show state
        state = agent.get_state()
        print(f"\n[ANALYSIS] Agent State:")
        print(f"  - Executions: {state.execution_count}")
        print(f"  - Messages: {len(state.messages)}")
        print(f"  - Current task: {state.current_task}")
        
        # Reset and show new state
        print("\n[INFO] Resetting agent...")
        agent.reset()
        
        new_state = agent.get_state()
        print(f"\n[ANALYSIS] State after reset:")
        print(f"  - Messages: {len(new_state.messages)}")
        print(f"  - Executions: {new_state.execution_count} (still tracks total)")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("[DEMO] AGENT EXAMPLES AND DEMONSTRATIONS")
    print("="*70)
    
    examples = [
        ("Simple Agent (Ollama)", example_simple_agent_ollama),
        ("Simple Agent (OpenAI)", example_simple_agent_openai),
        ("Multi-turn Conversation", example_multi_turn_conversation),
        ("Data Analyst Agent", example_data_analyst),
        ("Researcher Agent", example_researcher),
        ("State Management", example_state_management),
        ("Agent with Context", example_agent_with_context),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            await func()
        except Exception as e:
            logger.error(f"Example failed: {e}")
    
    # Sync example (can't be in async main)
    try:
        example_sync_agent()
    except Exception as e:
        logger.error(f"Sync example failed: {e}")
    
    print("\n" + "="*70)
    print("[DONE] All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n[START] Starting Agent Examples...\n")
    
    try:
        # Run async examples
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n[COMPLETE] Examples finished!\n")
