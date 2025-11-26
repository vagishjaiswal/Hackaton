"""
Simple Agent Implementations

This module provides concrete implementations of different agent types:
- DataAnalystAgent: Analyzes CSV data
- ResearcherAgent: Performs research and information gathering
- SimpleExecutorAgent: Generic task executor

Author: AI Assistant
Date: 2024-11-27
"""

import logging
from typing import Optional, Dict, Any

from .base_agent import BaseAgent, BaseTool


logger = logging.getLogger(__name__)


class DataAnalystAgent(BaseAgent):
    """
    Data Analyst Agent - Specialized for CSV data analysis.
    
    This agent can:
    - Load and explore CSV files
    - Perform statistical analysis
    - Generate insights from data
    - Answer questions about data
    
    Example:
        ```python
        agent = DataAnalystAgent(
            csv_file="data/input/sample_data.csv"
        )
        result = await agent.execute("Analyze the sales data")
        ```
    """
    
    def __init__(
        self,
        csv_file: Optional[str] = None,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        **kwargs
    ):
        """
        Initialize Data Analyst Agent.
        
        Args:
            csv_file: Path to CSV file to analyze
            llm_provider: LLM provider to use
            llm_model: Model name
            **kwargs: Additional arguments
        """
        # Default system prompt
        system_prompt = """You are a data analyst expert. Your role is to:
- Analyze CSV data and identify patterns
- Provide statistical insights
- Answer questions about the data
- Generate clear, actionable recommendations
- Think step-by-step through analysis

Be precise, concise, and data-driven in your responses."""
        
        super().__init__(
            name="DataAnalyst",
            role="data_analyst",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            llm_model=llm_model,
            **kwargs
        )
        
        # Set context for CSV file
        if csv_file:
            self.set_context({"csv_file": csv_file})
            self.logger.info(f"Data Analyst initialized with CSV: {csv_file}")
    
    async def execute(self, task: str, **kwargs) -> str:
        """
        Execute a data analysis task.
        
        Args:
            task: Analysis task description
            **kwargs: Additional arguments
            
        Returns:
            Analysis result
            
        Example:
            ```python
            result = await agent.execute(
                "What are the top 3 categories by sales?"
            )
            ```
        """
        try:
            self.logger.info(f"Executing task: {task}")
            self.state.current_task = task
            self.state.execution_count += 1
            
            # Add task to history
            self.add_to_history("user", task)
            
            # Get CSV file from context
            csv_file = self.get_context("csv_file")
            
            # Build enhanced prompt
            if csv_file:
                enhanced_prompt = f"""Please analyze the CSV file: {csv_file}

Task: {task}

Provide a detailed analysis."""
            else:
                enhanced_prompt = task
            
            # Generate response
            response = await self._generate_response(enhanced_prompt)
            
            # Store response
            self.add_to_history("assistant", response)
            self.state.last_response = response
            
            self.logger.info("Task completed successfully")
            return response
        
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            raise


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent - Specialized for research and information gathering.
    
    This agent can:
    - Perform web research
    - Gather and synthesize information
    - Answer complex questions
    - Provide citations and sources
    
    Example:
        ```python
        agent = ResearcherAgent()
        result = await agent.execute("Research the latest AI developments")
        ```
    """
    
    def __init__(
        self,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        **kwargs
    ):
        """
        Initialize Researcher Agent.
        
        Args:
            llm_provider: LLM provider to use
            llm_model: Model name
            **kwargs: Additional arguments
        """
        # Default system prompt
        system_prompt = """You are a research expert. Your role is to:
- Conduct thorough research on topics
- Gather and synthesize information
- Answer complex questions with depth
- Provide well-reasoned conclusions
- Cite sources when possible
- Think critically and ask clarifying questions

Focus on accuracy and comprehensive coverage."""
        
        super().__init__(
            name="Researcher",
            role="researcher",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            llm_model=llm_model,
            **kwargs
        )
        
        self.logger.info("Researcher Agent initialized")
    
    async def execute(self, task: str, **kwargs) -> str:
        """
        Execute a research task.
        
        Args:
            task: Research task description
            **kwargs: Additional arguments
            
        Returns:
            Research result
            
        Example:
            ```python
            result = await agent.execute(
                "What are the current trends in machine learning?"
            )
            ```
        """
        try:
            self.logger.info(f"Executing research task: {task}")
            self.state.current_task = task
            self.state.execution_count += 1
            
            # Add task to history
            self.add_to_history("user", task)
            
            # Generate response
            response = await self._generate_response(task)
            
            # Store response
            self.add_to_history("assistant", response)
            self.state.last_response = response
            
            self.logger.info("Research task completed")
            return response
        
        except Exception as e:
            self.logger.error(f"Error executing research task: {e}")
            raise


class SimpleExecutorAgent(BaseAgent):
    """
    Simple Executor Agent - Generic task executor.
    
    This agent can:
    - Execute various types of tasks
    - Answer questions
    - Provide solutions
    - Multi-step reasoning
    
    Example:
        ```python
        agent = SimpleExecutorAgent(
            system_prompt="You are a helpful coding assistant"
        )
        result = await agent.execute("Write a Python function to calculate factorial")
        ```
    """
    
    def __init__(
        self,
        system_prompt: str = "You are a helpful AI assistant. Provide clear, concise, and accurate responses.",
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        **kwargs
    ):
        """
        Initialize Simple Executor Agent.
        
        Args:
            system_prompt: Custom system prompt
            llm_provider: LLM provider to use
            llm_model: Model name
            **kwargs: Additional arguments
        """
        super().__init__(
            name="SimpleExecutor",
            role="executor",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            llm_model=llm_model,
            **kwargs
        )
        
        self.logger.info("Simple Executor Agent initialized")
    
    async def execute(self, task: str, **kwargs) -> str:
        """
        Execute a task.
        
        Args:
            task: Task description
            **kwargs: Additional arguments
            
        Returns:
            Task result
            
        Example:
            ```python
            result = await agent.execute("Explain quantum computing")
            ```
        """
        try:
            self.logger.info(f"Executing task: {task}")
            self.state.current_task = task
            self.state.execution_count += 1
            
            # Add task to history
            self.add_to_history("user", task)
            
            # Generate response
            response = await self._generate_response(task)
            
            # Store response
            self.add_to_history("assistant", response)
            self.state.last_response = response
            
            self.logger.info("Task completed")
            return response
        
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            raise


class SyncExecutorAgent(SimpleExecutorAgent):
    """
    Synchronous version of Simple Executor Agent.
    
    Uses synchronous methods instead of async.
    Better for Streamlit and other synchronous frameworks.
    
    Example:
        ```python
        agent = SyncExecutorAgent()
        result = agent.execute_sync("What is Python?")
        ```
    """
    
    def execute_sync(self, task: str, **kwargs) -> str:
        """
        Execute a task synchronously.
        
        Args:
            task: Task description
            **kwargs: Additional arguments
            
        Returns:
            Task result
        """
        try:
            self.logger.info(f"Executing task (sync): {task}")
            self.state.current_task = task
            self.state.execution_count += 1
            
            # Add task to history
            self.add_to_history("user", task)
            
            # Generate response
            response = self._generate_response_sync(task)
            
            # Store response
            self.add_to_history("assistant", response)
            self.state.last_response = response
            
            self.logger.info("Task completed (sync)")
            return response
        
        except Exception as e:
            self.logger.error(f"Error executing task (sync): {e}")
            raise
    
    async def execute(self, task: str, **kwargs) -> str:
        """
        Async wrapper for synchronous execution.
        """
        return self.execute_sync(task, **kwargs)
