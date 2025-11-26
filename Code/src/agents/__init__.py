"""
Agents Module

This module contains all agent implementations.

Available Agents:
- BaseAgent: Abstract base class for all agents
- DataAnalystAgent: CSV data analysis specialist
- ResearcherAgent: Research and information gathering
- SimpleExecutorAgent: Generic task executor
- SyncExecutorAgent: Synchronous task executor

Usage:
    from src.agents import SimpleExecutorAgent
    
    agent = SimpleExecutorAgent()
    result = await agent.execute("What is AI?")
"""

from .base_agent import (
    BaseAgent,
    BaseTool,
    AgentRole,
    AgentMessage,
    AgentState,
)
from .simple_agents import (
    DataAnalystAgent,
    ResearcherAgent,
    SimpleExecutorAgent,
    SyncExecutorAgent,
)

__all__ = [
    "BaseAgent",
    "BaseTool",
    "AgentRole",
    "AgentMessage",
    "AgentState",
    "DataAnalystAgent",
    "ResearcherAgent",
    "SimpleExecutorAgent",
    "SyncExecutorAgent",
]
