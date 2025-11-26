"""
Quick Reference Guide for Agent System

This file provides quick reference for common tasks.

Format: 
    # Task Name
    ```
    code example
    ```

Last Updated: 2024-11-27
"""

# =============================================================================
# QUICK START (Copy & Paste)
# =============================================================================

# 1. SIMPLE TASK (Most Common)
import asyncio
from src.agents import SimpleExecutorAgent

async def main():
    agent = SimpleExecutorAgent(llm_provider="ollama")
    result = await agent.execute("What is Python?")
    print(result)

asyncio.run(main())


# 2. SYNCHRONOUS (For Streamlit)
from src.agents import SyncExecutorAgent

agent = SyncExecutorAgent()
result = agent.execute_sync("What is AI?")
print(result)


# 3. DATA ANALYSIS
import asyncio
from src.agents import DataAnalystAgent

async def main():
    agent = DataAnalystAgent("data/input/sample_data.csv")
    result = await agent.execute("What is the average value?")
    print(result)

asyncio.run(main())


# 4. MULTI-TURN CONVERSATION
import asyncio
from src.agents import SimpleExecutorAgent

async def main():
    agent = SimpleExecutorAgent()
    
    await agent.execute("What is ML?")
    await agent.execute("Can you give an example?")
    await agent.execute("How is it used?")
    
    # Show history
    for msg in agent.get_history():
        print(f"{msg['role']}: {msg['content'][:50]}...")

asyncio.run(main())


# 5. COMPARE PROVIDERS
import asyncio
from src.agents import SimpleExecutorAgent

async def main():
    ollama_agent = SimpleExecutorAgent(llm_provider="ollama")
    openai_agent = SimpleExecutorAgent(llm_provider="openai")
    
    task = "Explain quantum computing"
    
    ollama_result = await ollama_agent.execute(task)
    openai_result = await openai_agent.execute(task)
    
    print("Ollama:", ollama_result[:100])
    print("OpenAI:", openai_result[:100])

asyncio.run(main())


# =============================================================================
# COMMON PATTERNS
# =============================================================================

# CUSTOM SYSTEM PROMPT
agent = SimpleExecutorAgent(
    system_prompt="You are a Python expert. Provide code examples."
)

# SET CONTEXT
agent.set_context({"user_id": "123", "project": "AI"})
value = agent.get_context("user_id")

# MANAGE TOOLS
from src.agents import BaseTool

class MyTool(BaseTool):
    def execute(self, **kwargs):
        return "result"

agent.register_tool(MyTool("tool1", "description"))
tools = agent.list_tools()
agent.unregister_tool("tool1")

# GET STATE
state = agent.get_state()
print(f"Executions: {state.execution_count}")
print(f"Messages: {len(state.messages)}")

# RESET CONVERSATION
agent.reset()

# GET HISTORY
all_history = agent.get_history()
recent = agent.get_history(last_k=5)

# EXPORT STATE
state_dict = agent.to_dict()


# =============================================================================
# PROVIDER SWITCHING
# =============================================================================

# OLLAMA (Local, Free)
agent = SimpleExecutorAgent(
    llm_provider="ollama",
    llm_model="llama2"
)

# OPENAI (Cloud)
agent = SimpleExecutorAgent(
    llm_provider="openai",
    llm_model="gpt-3.5-turbo"
)

# DIFFERENT MODELS
models = {
    "ollama": ["llama2", "mistral", "neural-chat", "phi"],
    "openai": ["gpt-4", "gpt-3.5-turbo"]
}


# =============================================================================
# ERROR HANDLING
# =============================================================================

try:
    agent = SimpleExecutorAgent()
    result = await agent.execute(task)
except ConnectionError:
    print("LLM provider not available")
except ValueError as e:
    print(f"Invalid configuration: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")


# =============================================================================
# TESTING
# =============================================================================

# RUN ALL TESTS
# pytest tests/test_agents.py -v

# SPECIFIC TEST
# pytest tests/test_agents.py::TestAgentInitialization -v

# WITH OUTPUT
# pytest tests/test_agents.py -v -s

# COVERAGE
# pytest tests/test_agents.py --cov=src/agents


# =============================================================================
# STREAMLIT INTEGRATION
# =============================================================================

import streamlit as st
from src.agents import SyncExecutorAgent

st.title("Agent Chat")

if "agent" not in st.session_state:
    st.session_state.agent = SyncExecutorAgent()

user_input = st.text_input("Ask me anything:")

if user_input:
    response = st.session_state.agent.execute_sync(user_input)
    st.write(response)


# =============================================================================
# FLASK INTEGRATION
# =============================================================================

from flask import Flask, request, jsonify
from src.agents import SyncExecutorAgent

app = Flask(__name__)
agent = SyncExecutorAgent()

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    task = data.get("task")
    
    result = agent.execute_sync(task)
    
    return jsonify({"result": result})


# =============================================================================
# BATCH PROCESSING
# =============================================================================

import asyncio
from src.agents import SimpleExecutorAgent

async def batch_process(tasks):
    agent = SimpleExecutorAgent()
    
    results = []
    for task in tasks:
        result = await agent.execute(task)
        results.append(result)
    
    return results

# Usage
tasks = ["What is AI?", "What is ML?", "What is DL?"]
results = asyncio.run(batch_process(tasks))


# =============================================================================
# AGENT COMPARISON
# =============================================================================

import asyncio
from src.agents import SimpleExecutorAgent

async def compare():
    agents = {
        "Ollama": SimpleExecutorAgent(llm_provider="ollama"),
        "OpenAI": SimpleExecutorAgent(llm_provider="openai")
    }
    
    task = "Your question"
    
    for name, agent in agents.items():
        result = await agent.execute(task)
        print(f"{name}: {result[:100]}")

asyncio.run(compare())


# =============================================================================
# LOGGING
# =============================================================================

import logging

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

agent = SimpleExecutorAgent(verbose=True)


# =============================================================================
# AGENT TYPES CHEAT SHEET
# =============================================================================

"""
SimpleExecutorAgent
├── Use for: General tasks, Q&A
├── Provider: Ollama (default) or OpenAI
├── Async: Yes
└── Example: General assistant

SyncExecutorAgent
├── Use for: Streamlit, Flask, Django
├── Provider: Ollama or OpenAI
├── Async: No (synchronous)
└── Example: Web app chatbot

DataAnalystAgent
├── Use for: CSV analysis, data insights
├── Provider: Ollama or OpenAI
├── Async: Yes
└── Example: Data question answering

ResearcherAgent
├── Use for: Research, information gathering
├── Provider: Ollama or OpenAI
├── Async: Yes
└── Example: Topic research
"""


# =============================================================================
# TROUBLESHOOTING
# =============================================================================

"""
Problem: "Cannot connect to Ollama"
Solution: 
  1. Start Ollama: ollama serve
  2. Check: curl http://localhost:11434/api/tags
  3. Pull model: ollama pull llama2

Problem: "OPENAI_API_KEY not found"
Solution:
  export OPENAI_API_KEY=sk-...

Problem: "Response is too slow"
Solution:
  1. Use faster model: phi, neural-chat
  2. Use OpenAI: gpt-3.5-turbo
  3. Reduce max_tokens
  
Problem: "Out of memory"
Solution:
  1. Reset: agent.reset()
  2. Limit history: agent.get_history(last_k=5)
"""


# =============================================================================
# USEFUL COMMANDS
# =============================================================================

"""
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_agents.py -v

# Run examples
python examples_agent_usage.py

# Start Ollama
ollama serve

# Pull Ollama model
ollama pull llama2

# List Ollama models
ollama list

# Check connectivity
curl http://localhost:11434/api/tags

# Run specific test
pytest tests/test_agents.py::TestAgentInitialization::test_agent_initialization -v
"""


# =============================================================================
# FILE PATHS
# =============================================================================

"""
src/agents/
├── base_agent.py              # Base classes, AgentState
├── simple_agents.py           # Pre-built agents
└── __init__.py               # Exports

tests/
└── test_agents.py            # 50+ tests

examples_agent_usage.py        # 8 complete examples
"""


# =============================================================================
# IMPORTS
# =============================================================================

"""
from src.agents import (
    BaseAgent,                 # Abstract base
    BaseTool,                  # Tool interface
    SimpleExecutorAgent,       # General executor
    SyncExecutorAgent,         # Synchronous executor
    DataAnalystAgent,          # CSV analyzer
    ResearcherAgent,           # Researcher
    AgentState,                # State tracking
    AgentMessage,              # Message class
    AgentRole                  # Role enum
)

from src.llm import (
    LLMProviderFactory,        # Create providers
    BaseLLMProvider,           # Base LLM class
    OpenAIProvider,            # OpenAI provider
    OllamaProvider             # Ollama provider
)

from src.tools import (
    CSVLoader                  # CSV data loading
)
"""


# =============================================================================
# ADVANCED PATTERNS
# =============================================================================

# AGENT PIPELINE
async def pipeline():
    researcher = SimpleExecutorAgent(
        system_prompt="You are a researcher"
    )
    analyst = SimpleExecutorAgent(
        system_prompt="You are an analyst"
    )
    
    # Step 1: Research
    research = await researcher.execute("Research topic X")
    
    # Step 2: Analyze
    analysis = await analyst.execute(
        f"Analyze this: {research}"
    )
    
    return analysis


# CONTEXT PASSING BETWEEN AGENTS
async def context_passing():
    agent1 = SimpleExecutorAgent()
    agent2 = SimpleExecutorAgent()
    
    # Agent 1 does work
    result1 = await agent1.execute("Task 1")
    
    # Pass context to agent 2
    agent2.set_context({"previous_result": result1})
    
    # Agent 2 uses context
    result2 = await agent2.execute("Task 2 (use context)")


# CONDITIONAL EXECUTION
async def conditional():
    agent = SimpleExecutorAgent()
    
    result = await agent.execute("Is Python good?")
    
    if "yes" in result.lower():
        next_result = await agent.execute("Why is Python good?")
    else:
        next_result = await agent.execute("What are its limitations?")
    
    return next_result


"""
Last Updated: November 27, 2024
Version: 1.0
Author: AI Assistant
"""
