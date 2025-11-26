"""
Base Agent Abstract Class

This module defines the abstract base class for all AI agents.
All specific agent implementations (DataAnalyst, Researcher, etc.) inherit from this class.

Features:
- Abstract interface for agent operations
- Tool management and registration
- State management for conversation history
- LLM provider integration via factory
- Logging and error handling
- Configuration-driven design

Author: AI Assistant
Date: 2024-11-27
"""

import logging
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

from src.llm import LLMProviderFactory, BaseLLMProvider


# Configure logging
logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Enum for different agent roles."""
    DATA_ANALYST = "data_analyst"
    RESEARCHER = "researcher"
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    REPORTER = "reporter"
    CUSTOM = "custom"


@dataclass
class AgentMessage:
    """Data class representing a message in agent conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return asdict(self)


@dataclass
class AgentState:
    """Data class representing agent's internal state."""
    agent_name: str
    messages: List[AgentMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    current_task: Optional[str] = None
    last_response: Optional[str] = None
    execution_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        state_dict = asdict(self)
        state_dict['messages'] = [msg.to_dict() for msg in self.messages]
        return state_dict
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the conversation history."""
        msg = AgentMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(msg)
    
    def clear_messages(self) -> None:
        """Clear all messages."""
        self.messages = []
    
    def get_last_k_messages(self, k: int = 5) -> List[Dict[str, str]]:
        """Get last k messages in conversation."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages[-k:]
        ]


class BaseTool(ABC):
    """Base class for agent tools."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize a tool.
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        pass
    
    def __repr__(self) -> str:
        return f"Tool({self.name}: {self.description})"


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Agents are autonomous units that can:
    - Interact with LLMs (OpenAI, Ollama, etc.)
    - Use tools to accomplish tasks
    - Maintain conversation state
    - Execute complex reasoning workflows
    
    Attributes:
        name: Agent identifier
        role: Agent role/type
        system_prompt: System instruction for the LLM
        llm: LLM provider instance
        tools: Registry of available tools
        state: Agent's conversation state
    
    Example:
        ```python
        class MyAgent(BaseAgent):
            async def execute(self, task: str) -> str:
                # Implementation
                pass
        
        agent = MyAgent(
            name="analyzer",
            system_prompt="You are a data analyst",
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        
        result = await agent.execute("Analyze this data")
        ```
    """
    
    def __init__(
        self,
        name: str,
        role: str = "custom",
        system_prompt: str = "",
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        llm_config: Optional[Dict[str, Any]] = None,
        tools: Optional[List[BaseTool]] = None,
        max_iterations: int = 5,
        verbose: bool = True
    ):
        """
        Initialize a base agent.
        
        Args:
            name: Agent name/identifier
            role: Agent role (data_analyst, researcher, etc.)
            system_prompt: System prompt for the LLM
            llm_provider: LLM provider ("openai", "ollama")
            llm_model: Model name (e.g., "gpt-4", "llama3.2")
            llm_config: Optional LLM configuration overrides
            tools: Optional list of tools available to agent
            max_iterations: Maximum iterations for agent loops
            verbose: Enable verbose logging
            
        Raises:
            ValueError: If required parameters are missing
            ConnectionError: If LLM provider connection fails
        """
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Agent name cannot be empty")
        
        if not system_prompt or not system_prompt.strip():
            raise ValueError("System prompt cannot be empty")
        
        # Store configuration
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Initialize logger
        self.logger = logging.getLogger(f"Agent.{self.name}")
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        
        # Initialize LLM provider
        try:
            self.llm = self._initialize_llm(
                llm_provider,
                llm_model,
                llm_config
            )
            self.logger.info(
                f"Agent '{self.name}' initialized with "
                f"{llm_provider}/{llm_model}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {e}")
            raise
        
        # Initialize tools
        self.tools: Dict[str, BaseTool] = {}
        if tools:
            for tool in tools:
                self.register_tool(tool)
        
        # Initialize state
        self.state = AgentState(agent_name=self.name)
        
        # Add system prompt to initial state
        self.state.add_message(
            role="system",
            content=self.system_prompt,
            metadata={"type": "system"}
        )
        
        self.logger.info(
            f"Agent '{self.name}' ready with {len(self.tools)} tools"
        )
    
    def _initialize_llm(
        self,
        provider: str,
        model: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMProvider:
        """
        Initialize LLM provider using factory.
        
        Args:
            provider: Provider name
            model: Model name
            config: Optional configuration
            
        Returns:
            Initialized LLM provider
        """
        self.logger.debug(f"Initializing {provider} provider with {model}")
        
        llm = LLMProviderFactory.create(
            provider_type=provider,
            model=model,
            **config if config else {}
        )
        
        return llm
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool for use by this agent.
        
        Args:
            tool: Tool instance
            
        Example:
            ```python
            csv_tool = CSVLoaderTool()
            agent.register_tool(csv_tool)
            ```
        """
        if not isinstance(tool, BaseTool):
            raise TypeError(f"Tool must inherit from BaseTool, got {type(tool)}")
        
        self.tools[tool.name] = tool
        self.logger.debug(f"Registered tool: {tool.name}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of tool to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.debug(f"Unregistered tool: {tool_name}")
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a registered tool by name.
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        List all available tools.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_state(self) -> AgentState:
        """
        Get current agent state.
        
        Returns:
            Current state
        """
        return self.state
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """
        Set agent context (shared data).
        
        Args:
            context: Context dictionary
            
        Example:
            ```python
            agent.set_context({
                "csv_file": "data.csv",
                "analysis_type": "statistical"
            })
            ```
        """
        self.state.context.update(context)
        self.logger.debug(f"Context updated: {context.keys()}")
    
    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Get agent context.
        
        Args:
            key: Specific context key (optional)
            
        Returns:
            Full context or specific value
        """
        if key:
            return self.state.context.get(key)
        return self.state.context
    
    def reset(self) -> None:
        """
        Reset agent state.
        
        Clears conversation history but keeps system prompt.
        """
        self.logger.info("Resetting agent state")
        self.state.clear_messages()
        self.state.add_message(
            role="system",
            content=self.system_prompt,
            metadata={"type": "system"}
        )
    
    async def _generate_response(
        self,
        prompt: str,
        use_history: bool = True
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            use_history: Whether to use conversation history
            
        Returns:
            LLM response
        """
        try:
            if use_history:
                # Use full conversation history
                messages = self.state.get_conversation_history()
                messages.append({"role": "user", "content": prompt})
                response = await self.llm.generate_with_messages(messages)
            else:
                # Use just the current prompt with system prompt
                response = await self.llm.generate(
                    prompt,
                    system_prompt=self.system_prompt
                )
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            raise
    
    def _generate_response_sync(
        self,
        prompt: str,
        use_history: bool = True
    ) -> str:
        """
        Synchronous version of _generate_response.
        
        Args:
            prompt: User prompt
            use_history: Whether to use conversation history
            
        Returns:
            LLM response
        """
        try:
            if use_history:
                # Use full conversation history
                messages = self.state.get_conversation_history()
                messages.append({"role": "user", "content": prompt})
                
                # For Ollama, use generate_sync
                # For OpenAI, we need to handle async differently
                if hasattr(self.llm, 'generate_sync'):
                    # Build prompt with history
                    full_prompt = "\n".join(
                        f"{m['role']}: {m['content']}"
                        for m in messages
                    )
                    response = self.llm.generate_sync(
                        full_prompt,
                        system_prompt=self.system_prompt
                    )
                else:
                    response = self.llm.generate_sync(
                        prompt,
                        system_prompt=self.system_prompt
                    )
            else:
                response = self.llm.generate_sync(
                    prompt,
                    system_prompt=self.system_prompt
                )
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error in synchronous generation: {e}")
            raise
    
    def add_to_history(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a message to conversation history.
        
        Args:
            role: Message role ("user", "assistant", "system")
            content: Message content
            metadata: Optional metadata
        """
        self.state.add_message(role, content, metadata)
    
    def get_history(self, last_k: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Args:
            last_k: Get only last k messages (optional)
            
        Returns:
            List of messages
        """
        if last_k:
            return self.state.get_last_k_messages(last_k)
        return self.state.get_conversation_history()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to dictionary representation.
        
        Returns:
            Dictionary with agent info
        """
        return {
            "name": self.name,
            "role": self.role,
            "system_prompt": self.system_prompt,
            "tools": self.list_tools(),
            "state": self.state.to_dict(),
            "llm_provider": self.llm.provider_name if self.llm else "mock",
            "llm_config": self.llm.get_config() if self.llm else {}
        }
    
    def __repr__(self) -> str:
        """String representation of agent."""
        provider = self.llm.provider_name if self.llm else "mock"
        return (
            f"Agent(name={self.name}, role={self.role}, "
            f"provider={provider}, "
            f"tools={len(self.tools)})"
        )
    
    @abstractmethod
    async def execute(self, task: str, **kwargs) -> str:
        """
        Execute a task. Must be implemented by subclasses.
        
        Args:
            task: Task description
            **kwargs: Additional arguments
            
        Returns:
            Task result
        """
        pass
