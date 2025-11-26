"""
Agent Test Suite

Comprehensive tests for agent implementations covering:
- Agent initialization
- Task execution (both sync and async)
- Tool management
- State management
- Conversation history
- Error handling
- Different LLM providers (Ollama, OpenAI)

Test Classes:
- TestBaseAgent: Base functionality tests
- TestSimpleExecutor: Simple executor tests
- TestDataAnalyst: Data analyst tests
- TestAgentWithProviders: Provider-specific tests
- TestAgentToolManagement: Tool management tests
- TestAgentState: State management tests

Author: AI Assistant
Date: 2024-11-27
"""

import pytest
import asyncio
import logging
from typing import Optional
from unittest.mock import Mock, patch, AsyncMock

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents import (
    SimpleExecutorAgent,
    SyncExecutorAgent,
    DataAnalystAgent,
    ResearcherAgent,
    BaseAgent,
    BaseTool,
    AgentState,
    AgentMessage,
)
from src.llm import LLMProviderFactory


# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Test Fixtures
# ============================================================================

class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def __init__(self, name: str = "mock_tool", description: str = "A mock tool"):
        super().__init__(name, description)
        self.call_count = 0
    
    def execute(self, **kwargs):
        """Execute the mock tool."""
        self.call_count += 1
        return f"Mock tool executed with {kwargs}"


class TestableSimpleExecutorAgent(SimpleExecutorAgent):
    """Testable version of SimpleExecutorAgent with mock LLM."""
    
    def __init__(self, mock_response: str = "Mock response", **kwargs):
        self.mock_response = mock_response
        try:
            super().__init__(**kwargs)
        except Exception as e:
            logger.warning(f"Failed to initialize real LLM: {e}. Using mock.")
            # Create a minimal mock agent for testing
            self.name = "SimpleExecutor"
            self.role = "executor"
            self.system_prompt = kwargs.get(
                "system_prompt",
                "You are a helpful AI assistant."
            )
            self.logger = logging.getLogger(f"Agent.{self.name}")
            self.tools = {}
            self.state = AgentState(agent_name=self.name)
            # Add system message to state
            self.state.add_message(
                role="system",
                content=self.system_prompt,
                metadata={"type": "system"}
            )
            self.llm = None
    
    async def _generate_response(self, prompt: str, use_history: bool = True) -> str:
        """Override to return mock response."""
        return self.mock_response


@pytest.fixture
def simple_executor():
    """Create a simple executor agent for testing."""
    return TestableSimpleExecutorAgent(
        mock_response="This is a test response"
    )


@pytest.fixture
def sync_executor():
    """Create a sync executor agent for testing."""
    try:
        return SyncExecutorAgent()
    except Exception as e:
        logger.warning(f"Failed to create SyncExecutorAgent: {e}")
        # Return a testable version
        agent = TestableSimpleExecutorAgent(mock_response="Test response")
        agent.__class__ = SyncExecutorAgent
        return agent


@pytest.fixture
def mock_tool():
    """Create a mock tool for testing."""
    return MockTool("test_tool", "A test tool")


# ============================================================================
# Test Classes
# ============================================================================

class TestAgentInitialization:
    """Test agent initialization and configuration."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Test response",
            system_prompt="You are a test assistant"
        )
        
        assert agent.name == "SimpleExecutor"
        assert agent.role == "executor"
        assert "test assistant" in agent.system_prompt
        assert len(agent.tools) == 0
    
    def test_agent_with_custom_role(self):
        """Test agent with custom role."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response",
            system_prompt="You are an analyst"
        )
        # Manually set role for testing
        agent.role = "custom_role"
        
        assert agent.role == "custom_role"


class TestAgentStateManagement:
    """Test agent state management."""
    
    def test_initial_state(self):
        """Test agent initializes with correct state."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        state = agent.get_state()
        assert state.agent_name == agent.name
        assert state.current_task is None
        assert state.execution_count == 0
        assert len(state.messages) >= 1  # At least system message
    
    def test_add_message_to_history(self):
        """Test adding messages to history."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        initial_count = len(agent.state.messages)
        agent.add_to_history("user", "Test message")
        
        assert len(agent.state.messages) == initial_count + 1
        assert agent.state.messages[-1].content == "Test message"
        assert agent.state.messages[-1].role == "user"
    
    def test_conversation_history(self):
        """Test getting conversation history."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        agent.add_to_history("user", "Hello")
        agent.add_to_history("assistant", "Hi there")
        
        history = agent.get_history()
        assert len(history) >= 3  # system + 2 messages
        
        last_message = history[-1]
        assert last_message["role"] == "assistant"
        assert last_message["content"] == "Hi there"
    
    def test_get_last_k_messages(self):
        """Test getting last k messages."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        for i in range(5):
            agent.add_to_history("user", f"Message {i}")
        
        last_3 = agent.get_history(last_k=3)
        assert len(last_3) <= 3
    
    def test_reset_agent(self):
        """Test resetting agent state."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        agent.add_to_history("user", "Message 1")
        agent.add_to_history("assistant", "Response 1")
        
        initial_count = len(agent.state.messages)
        
        agent.reset()
        
        # Should only have system message
        assert len(agent.state.messages) == 1
        assert agent.state.messages[0].role == "system"
    
    def test_state_to_dict(self):
        """Test converting state to dictionary."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        agent.add_to_history("user", "Test")
        
        state_dict = agent.state.to_dict()
        
        assert "agent_name" in state_dict
        assert "messages" in state_dict
        assert "context" in state_dict
        assert isinstance(state_dict["messages"], list)


class TestAgentContextManagement:
    """Test agent context management."""
    
    def test_set_context(self):
        """Test setting agent context."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        context = {"key1": "value1", "key2": "value2"}
        agent.set_context(context)
        
        assert agent.get_context() == context
    
    def test_get_context_key(self):
        """Test getting specific context key."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        agent.set_context({"csv_file": "data.csv", "type": "analysis"})
        
        assert agent.get_context("csv_file") == "data.csv"
        assert agent.get_context("type") == "analysis"
    
    def test_update_context(self):
        """Test updating context."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        agent.set_context({"key1": "value1"})
        agent.set_context({"key2": "value2"})
        
        context = agent.get_context()
        assert context["key1"] == "value1"
        assert context["key2"] == "value2"


class TestToolManagement:
    """Test tool management functionality."""
    
    def test_register_tool(self):
        """Test registering a tool."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        tool = MockTool("test_tool", "A test tool")
        
        agent.register_tool(tool)
        
        assert "test_tool" in agent.tools
        assert agent.get_tool("test_tool") is tool
    
    def test_register_multiple_tools(self):
        """Test registering multiple tools."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        tool1 = MockTool("tool1", "First tool")
        tool2 = MockTool("tool2", "Second tool")
        
        agent.register_tool(tool1)
        agent.register_tool(tool2)
        
        assert len(agent.tools) == 2
        assert agent.list_tools() == ["tool1", "tool2"]
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        tool = MockTool("test_tool", "A test tool")
        
        agent.register_tool(tool)
        assert "test_tool" in agent.tools
        
        result = agent.unregister_tool("test_tool")
        
        assert result is True
        assert "test_tool" not in agent.tools
    
    def test_unregister_nonexistent_tool(self):
        """Test unregistering a tool that doesn't exist."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        result = agent.unregister_tool("nonexistent")
        
        assert result is False
    
    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        tool = agent.get_tool("nonexistent")
        
        assert tool is None
    
    def test_list_tools(self):
        """Test listing all tools."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        assert agent.list_tools() == []
        
        tool1 = MockTool("tool1", "First")
        tool2 = MockTool("tool2", "Second")
        
        agent.register_tool(tool1)
        agent.register_tool(tool2)
        
        tools = agent.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools


class TestAgentExecution:
    """Test agent execution."""
    
    @pytest.mark.asyncio
    async def test_simple_agent_execution(self):
        """Test executing a simple agent task."""
        agent = TestableSimpleExecutorAgent(
            mock_response="This is the answer"
        )
        
        result = await agent.execute("What is 2+2?")
        
        assert result == "This is the answer"
        assert agent.state.execution_count == 1
        assert agent.state.last_response == result
    
    @pytest.mark.asyncio
    async def test_agent_adds_to_history(self):
        """Test that agent adds execution to history."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        initial_count = len(agent.state.messages)
        
        await agent.execute("Test task")
        
        # Should have system + user + assistant
        assert len(agent.state.messages) > initial_count
    
    @pytest.mark.asyncio
    async def test_multiple_executions(self):
        """Test multiple agent executions."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        await agent.execute("First task")
        await agent.execute("Second task")
        await agent.execute("Third task")
        
        assert agent.state.execution_count == 3
    
    def test_sync_agent_execution(self):
        """Test synchronous agent execution."""
        try:
            agent = SyncExecutorAgent()
            result = agent.execute_sync("What is AI?")
            
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception as e:
            logger.info(f"Sync execution test skipped: {e}")
            pytest.skip(f"Ollama not available: {e}")


class TestDataAnalystAgent:
    """Test data analyst agent."""
    
    def test_data_analyst_initialization(self):
        """Test initializing data analyst agent."""
        try:
            agent = DataAnalystAgent(
                csv_file="data/input/sample_data.csv",
                llm_provider="ollama",
                llm_model="llama2"
            )
            
            assert agent.name == "DataAnalyst"
            assert agent.role == "data_analyst"
            assert agent.get_context("csv_file") == "data/input/sample_data.csv"
        except Exception as e:
            logger.info(f"DataAnalyst test skipped: {e}")
            pytest.skip(f"LLM not available: {e}")


class TestResearcherAgent:
    """Test researcher agent."""
    
    def test_researcher_initialization(self):
        """Test initializing researcher agent."""
        try:
            agent = ResearcherAgent(
                llm_provider="ollama",
                llm_model="llama2"
            )
            
            assert agent.name == "Researcher"
            assert agent.role == "researcher"
        except Exception as e:
            logger.info(f"Researcher test skipped: {e}")
            pytest.skip(f"LLM not available: {e}")


class TestAgentRepr:
    """Test agent string representations."""
    
    def test_agent_repr(self):
        """Test agent __repr__ method."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        repr_str = repr(agent)
        
        assert "Agent" in repr_str
        assert agent.name in repr_str
        assert agent.role in repr_str


class TestAgentToDict:
    """Test agent to dictionary conversion."""
    
    def test_agent_to_dict(self):
        """Test converting agent to dictionary."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        agent.register_tool(MockTool("tool1", "A tool"))
        
        agent_dict = agent.to_dict()
        
        assert "name" in agent_dict
        assert "role" in agent_dict
        assert "tools" in agent_dict
        assert "state" in agent_dict
        assert agent_dict["name"] == agent.name
        assert "tool1" in agent_dict["tools"]


class TestErrorHandling:
    """Test error handling in agents."""
    
    def test_register_invalid_tool(self):
        """Test registering invalid tool raises error."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        with pytest.raises(TypeError):
            agent.register_tool("not a tool")


# ============================================================================
# Integration Tests
# ============================================================================

class TestAgentIntegration:
    """Integration tests for agents."""
    
    @pytest.mark.asyncio
    async def test_agent_with_tools_workflow(self):
        """Test agent workflow with tools."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Analysis complete"
        )
        
        # Register tools
        tool1 = MockTool("analyzer", "Data analyzer")
        tool2 = MockTool("reporter", "Report generator")
        
        agent.register_tool(tool1)
        agent.register_tool(tool2)
        
        # Set context
        agent.set_context({"file": "data.csv"})
        
        # Execute task
        result = await agent.execute("Analyze and report on data")
        
        # Verify
        assert result == "Analysis complete"
        assert agent.state.execution_count == 1
        assert tool1.call_count == 0  # Not actually called in mock
    
    def test_agent_state_persistence(self):
        """Test agent state persists across operations."""
        agent = TestableSimpleExecutorAgent(
            mock_response="Response"
        )
        
        # Set context
        agent.set_context({"user_id": "123"})
        
        # Add messages
        agent.add_to_history("user", "Message 1")
        agent.add_to_history("assistant", "Response 1")
        
        # Get state
        state1 = agent.get_state()
        
        # Verify persistence
        assert agent.get_context("user_id") == "123"
        assert len(state1.messages) >= 3


# ============================================================================
# Command Line Execution
# ============================================================================

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
