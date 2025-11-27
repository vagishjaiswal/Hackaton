"""
Chat-Based Workflow with Sequence Evaluator

This module implements an interactive chat-based workflow that:
1. Takes user task/goal
2. Uses Sequence Evaluator to generate execution plan
3. Asks user for clarifications if needed
4. Executes the sequence step-by-step
5. Provides results back to user

Features:
- Interactive clarification handling
- Dynamic sequence execution
- Step-by-step progress tracking
- Error recovery
- Result aggregation

Author: AI Assistant
Date: 2024-11-28
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.agents.simple_agents import (
    DataAnalystAgent,
    ResearcherAgent,
    SimpleExecutorAgent
)
from src.tools.csv_tools import CSVLoader


logger = logging.getLogger(__name__)


@dataclass
class WorkflowMessage:
    """Chat message in the workflow."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """State of the chat-based workflow."""
    task: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    sequence: List[Dict[str, Any]] = field(default_factory=list)
    clarifications: List[Dict[str, Any]] = field(default_factory=list)
    conversation: List[WorkflowMessage] = field(default_factory=list)
    current_step: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "initialized"  # initialized, clarifying, executing, completed, error
    error: Optional[str] = None


class ChatBasedWorkflow:
    """
    Interactive chat-based workflow with sequence evaluation.
    
    This workflow:
    1. Accepts user task via chat
    2. Evaluates and generates execution sequence
    3. Interactively asks for clarifications
    4. Executes sequence step-by-step
    5. Returns results
    
    Example:
        ```python
        workflow = ChatBasedWorkflow()
        
        # User provides task
        response = await workflow.process_message(
            "Analyze sales data from Q4 2024"
        )
        
        # If clarifications needed
        if workflow.needs_clarification():
            clarifications = workflow.get_clarifications()
            # Show questions to user
            
            # User answers
            await workflow.provide_clarifications({
                "csv_file": "sales_q4_2024.csv",
                "analysis_type": "summary"
            })
        
        # Execute
        result = await workflow.execute_sequence()
        ```
    """
    
    def __init__(
        self,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        data_dir: str = "data/input",
        verbose: bool = True
    ):
        """
        Initialize Chat-Based Workflow.
        
        Args:
            llm_provider: LLM provider to use
            llm_model: Model name
            data_dir: Directory for data files
            verbose: Enable verbose logging
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.data_dir = Path(data_dir)
        self.verbose = verbose
        
        # Initialize state
        self.state = WorkflowState()
        
        # Initialize sequence evaluator (import inside to avoid circular imports)
        from src.agents.sequence_evaluator import SequenceEvaluatorAgent
        
        self.evaluator = SequenceEvaluatorAgent(
            llm_provider=llm_provider,
            llm_model=llm_model,
            verbose=verbose
        )
        
        # Registry for available agents
        self.agent_registry: Dict[str, Callable] = {}
        self.tool_registry: Dict[str, Callable] = {}
        
        # Register default agents and tools
        self._register_defaults()
        
        logger.info("Chat-Based Workflow initialized")
    
    def _register_defaults(self) -> None:
        """Register default agents and tools."""
        # Register agents
        self.register_agent(
            "DataAnalyst",
            "Analyzes CSV data, generates insights, answers data questions",
            DataAnalystAgent
        )
        
        self.register_agent(
            "Researcher",
            "Performs research, gathers information, answers complex questions",
            ResearcherAgent
        )
        
        self.register_agent(
            "SimpleExecutor",
            "General purpose task executor, answers questions, solves problems",
            SimpleExecutorAgent
        )
        
        # Register tools
        self.register_tool(
            "CSVLoader",
            "Loads, validates, and queries CSV files",
            self._use_csv_loader
        )
        
        logger.debug("Default agents and tools registered")
    
    def register_agent(
        self,
        name: str,
        description: str,
        agent_class: type
    ) -> None:
        """
        Register an agent for use in sequences.
        
        Args:
            name: Agent name
            description: What the agent does
            agent_class: Agent class
        """
        self.agent_registry[name] = agent_class
        self.evaluator.register_available_agent(name, description)
        logger.debug(f"Registered agent: {name}")
    
    def register_tool(
        self,
        name: str,
        description: str,
        tool_function: Callable
    ) -> None:
        """
        Register a tool for use in sequences.
        
        Args:
            name: Tool name
            description: What the tool does
            tool_function: Function to execute the tool
        """
        self.tool_registry[name] = tool_function
        self.evaluator.register_available_tool(name, description)
        logger.debug(f"Registered tool: {name}")
    
    async def process_message(self, message: str) -> str:
        """
        Process a user message.
        
        Args:
            message: User message
            
        Returns:
            Response to user
        """
        try:
            # Add to conversation
            self._add_message("user", message)
            
            # If this is initial task
            if self.state.status == "initialized":
                return await self._handle_initial_task(message)
            
            # If providing clarifications
            elif self.state.status == "clarifying":
                return await self._handle_clarification_response(message)
            
            # If executing
            elif self.state.status == "executing":
                return "Workflow is currently executing. Please wait..."
            
            # If completed
            elif self.state.status == "completed":
                return await self._handle_new_task(message)
            
            else:
                return "Workflow is in an unknown state. Please restart."
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.state.status = "error"
            self.state.error = str(e)
            return f"Error: {e}"
    
    async def _handle_initial_task(self, task: str) -> str:
        """
        Handle initial task from user.
        
        Args:
            task: User task description
            
        Returns:
            Response with either clarifications or execution start
        """
        logger.info(f"Processing initial task: {task}")
        
        # Store task
        self.state.task = task
        
        # Evaluate sequence
        evaluation = await self.evaluator.evaluate_sequence(
            task=task,
            context=self.state.context
        )
        
        # Store sequence
        self.state.sequence = evaluation.get("sequence", [])
        self.state.clarifications = evaluation.get("clarifications", [])
        
        # Check if we need clarifications
        required_clarifications = [
            c for c in self.state.clarifications
            if c.get("required", True)
        ]
        
        if required_clarifications:
            # Need clarifications
            self.state.status = "clarifying"
            response = self._format_clarification_request(required_clarifications)
            self._add_message("assistant", response)
            return response
        
        elif not evaluation.get("can_execute", False):
            # Cannot execute
            response = self._format_cannot_execute(evaluation)
            self._add_message("assistant", response)
            return response
        
        else:
            # Can execute immediately
            self.state.status = "executing"
            response = f"Understood! I'll execute the following sequence:\n\n"
            response += self._format_sequence_preview(self.state.sequence)
            response += "\n\nStarting execution..."
            self._add_message("assistant", response)
            
            # Execute
            result = await self.execute_sequence()
            return result
    
    async def _handle_clarification_response(self, message: str) -> str:
        """
        Handle user's response to clarification questions.
        
        Args:
            message: User response
            
        Returns:
            Next response
        """
        logger.info("Processing clarification response")
        
        # Try to parse as structured data or natural language
        try:
            # Try JSON first
            clarifications_data = json.loads(message)
        except json.JSONDecodeError:
            # Parse natural language response with LLM
            clarifications_data = await self._parse_clarification_nlp(message)
        
        # Update context
        self.state.context.update(clarifications_data)
        
        # Re-evaluate with new context
        evaluation = await self.evaluator.evaluate_sequence(
            task=self.state.task,
            context=self.state.context
        )
        
        self.state.sequence = evaluation.get("sequence", [])
        self.state.clarifications = evaluation.get("clarifications", [])
        
        # Check if still need clarifications
        remaining = [
            c for c in self.state.clarifications
            if c.get("required", True) and c.get("field") not in self.state.context
        ]
        
        if remaining:
            response = "Thank you! I still need a few more details:\n\n"
            response += self._format_clarification_request(remaining)
            self._add_message("assistant", response)
            return response
        
        elif not evaluation.get("can_execute", False):
            response = self._format_cannot_execute(evaluation)
            self._add_message("assistant", response)
            return response
        
        else:
            # Ready to execute
            self.state.status = "executing"
            response = f"Perfect! I have all the information I need.\n\n"
            response += self._format_sequence_preview(self.state.sequence)
            response += "\n\nStarting execution..."
            self._add_message("assistant", response)
            
            result = await self.execute_sequence()
            return result
    
    async def _parse_clarification_nlp(self, message: str) -> Dict[str, Any]:
        """
        Parse natural language clarification response using LLM.
        
        Args:
            message: User message
            
        Returns:
            Extracted data
        """
        # Use simple executor to parse
        executor = SimpleExecutorAgent(
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            system_prompt="You extract structured data from natural language."
        )
        
        questions = self.state.clarifications
        questions_text = "\n".join([
            f"- {q['question']} (field: {q['field']})"
            for q in questions
        ])
        
        prompt = f"""Given these questions:
{questions_text}

User answered:
{message}

Extract the answers as JSON: {{"field_name": "value"}}

Return ONLY the JSON object."""
        
        response = await executor.execute(prompt)
        
        # Parse JSON
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1:
                return json.loads(response[json_start:json_end])
        except:
            pass
        
        # Fallback: return message as generic answer
        return {"user_response": message}
    
    async def _handle_new_task(self, message: str) -> str:
        """
        Handle new task after previous completion.
        
        Args:
            message: User message
            
        Returns:
            Response
        """
        # Reset state
        self.state = WorkflowState()
        
        # Process as initial task
        return await self._handle_initial_task(message)
    
    async def execute_sequence(self) -> str:
        """
        Execute the planned sequence.
        
        Returns:
            Execution result summary
        """
        try:
            logger.info(f"Executing sequence with {len(self.state.sequence)} steps")
            
            results = []
            
            for step_idx, step in enumerate(self.state.sequence):
                self.state.current_step = step_idx + 1
                
                logger.info(f"Executing step {self.state.current_step}: {step.get('step_name')}")
                
                # Execute step
                step_result = await self._execute_step(step)
                
                results.append({
                    "step": self.state.current_step,
                    "step_name": step.get("step_name"),
                    "status": "completed" if not step_result.get("error") else "error",
                    "result": step_result
                })
                
                # Update context with outputs
                if "outputs" in step_result:
                    self.state.context.update(step_result["outputs"])
                
                # Check for errors
                if step_result.get("error"):
                    logger.error(f"Step {self.state.current_step} failed: {step_result['error']}")
                    break
            
            # Store results
            self.state.results = results
            self.state.status = "completed"
            
            # Format response
            response = self._format_execution_result(results)
            self._add_message("assistant", response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error executing sequence: {e}")
            self.state.status = "error"
            self.state.error = str(e)
            return f"Execution failed: {e}"
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step.
        
        Args:
            step: Step definition
            
        Returns:
            Step result
        """
        try:
            agent_or_tool = step.get("agent_or_tool")
            action = step.get("action")
            inputs = step.get("inputs", {})
            
            # Replace context variables in inputs
            resolved_inputs = self._resolve_inputs(inputs)
            
            # Check if it's an agent or tool
            if agent_or_tool in self.agent_registry:
                result = await self._execute_agent_step(
                    agent_or_tool,
                    action,
                    resolved_inputs
                )
            elif agent_or_tool in self.tool_registry:
                result = await self._execute_tool_step(
                    agent_or_tool,
                    action,
                    resolved_inputs
                )
            else:
                result = {
                    "error": f"Unknown agent/tool: {agent_or_tool}"
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Error in step execution: {e}")
            return {"error": str(e)}
    
    async def _execute_agent_step(
        self,
        agent_name: str,
        action: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an agent step."""
        try:
            agent_class = self.agent_registry[agent_name]
            
            # Separate agent initialization parameters from task inputs
            agent_init_params = {
                "llm_provider": self.llm_provider,
                "llm_model": self.llm_model,
            }
            
            # Add known parameters from inputs (e.g., csv_file for DataAnalystAgent)
            known_agent_params = {"csv_file"}
            for key, value in inputs.items():
                if key in known_agent_params:
                    agent_init_params[key] = value
            
            # Create agent instance
            agent = agent_class(**agent_init_params)
            
            # Prepare task inputs (for the execute method, not constructor)
            task_inputs = {k: v for k, v in inputs.items() if k not in known_agent_params}
            
            # If no task inputs, use action as the task
            task = action if task_inputs == {} else str(task_inputs)
            
            # Execute
            result = await agent.execute(task)
            
            return {
                "agent": agent_name,
                "action": action,
                "result": result,
                "outputs": {"last_result": result}
            }
        
        except Exception as e:
            logger.error(f"Agent step error: {e}")
            return {"error": str(e)}
    
    async def _execute_tool_step(
        self,
        tool_name: str,
        action: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool step."""
        try:
            tool_func = self.tool_registry[tool_name]
            
            # Execute tool
            result = await tool_func(**inputs)
            
            return {
                "tool": tool_name,
                "action": action,
                "result": result,
                "outputs": {"last_result": result}
            }
        
        except Exception as e:
            logger.error(f"Tool step error: {e}")
            return {"error": str(e)}
    
    def _resolve_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve context variables in inputs.
        
        Args:
            inputs: Raw inputs with potential ${variable} references
            
        Returns:
            Resolved inputs
        """
        resolved = {}
        
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Extract variable name
                var_name = value[2:-1]
                resolved[key] = self.state.context.get(var_name, value)
            else:
                resolved[key] = value
        
        return resolved
    
    async def _use_csv_loader(self, csv_file: str, **kwargs) -> Any:
        """Tool function for CSVLoader."""
        file_path = self.data_dir / csv_file
        loader = CSVLoader(file_path)
        loader.load()
        
        # Store in context
        self.state.context["csv_data"] = loader.to_dict()
        self.state.context["csv_metadata"] = loader.get_metadata()
        
        return loader.get_summary()
    
    def _add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add message to conversation."""
        msg = WorkflowMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.state.conversation.append(msg)
    
    def _format_clarification_request(self, clarifications: List[Dict]) -> str:
        """Format clarification questions for user."""
        response = "I need some clarification to proceed:\n\n"
        
        for i, c in enumerate(clarifications, 1):
            question = c.get("question")
            options = c.get("options")
            required = c.get("required", True)
            
            response += f"{i}. {question}"
            if not required:
                response += " (optional)"
            
            if options:
                response += f"\n   Options: {', '.join(options)}"
            
            response += "\n\n"
        
        response += "You can answer in natural language or provide structured data as JSON."
        
        return response
    
    def _format_sequence_preview(self, sequence: List[Dict]) -> str:
        """Format sequence preview for user."""
        preview = "Execution Plan:\n"
        
        for step in sequence:
            step_num = step.get("step_number")
            step_name = step.get("step_name")
            agent_or_tool = step.get("agent_or_tool")
            action = step.get("action")
            
            preview += f"\n{step_num}. {step_name}"
            preview += f"\n   Using: {agent_or_tool}"
            preview += f"\n   Action: {action}\n"
        
        return preview
    
    def _format_cannot_execute(self, evaluation: Dict) -> str:
        """Format message when execution is not possible."""
        response = "I'm unable to complete this task because:\n\n"
        
        missing = evaluation.get("missing_capabilities", [])
        if missing:
            response += "Missing capabilities:\n"
            for cap in missing:
                response += f"- {cap}\n"
        
        reasoning = evaluation.get("reasoning", "")
        if reasoning:
            response += f"\nReasoning: {reasoning}"
        
        return response
    
    def _format_execution_result(self, results: List[Dict]) -> str:
        """Format execution results for user."""
        response = "✓ Execution completed!\n\n"
        response += f"Completed {len(results)} steps:\n\n"
        
        for result in results:
            step_num = result.get("step")
            step_name = result.get("step_name")
            status = result.get("status")
            
            emoji = "✓" if status == "completed" else "✗"
            response += f"{emoji} Step {step_num}: {step_name}\n"
            
            if status == "error":
                error = result.get("result", {}).get("error")
                response += f"   Error: {error}\n"
        
        # Add final result if available
        if results and results[-1].get("status") == "completed":
            last_result = results[-1].get("result", {}).get("result")
            if last_result:
                response += f"\n--- Final Result ---\n{last_result}"
        
        return response
    
    def needs_clarification(self) -> bool:
        """Check if workflow needs clarification."""
        return self.state.status == "clarifying"
    
    def get_clarifications(self) -> List[Dict]:
        """Get pending clarifications."""
        return self.state.clarifications
    
    def get_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return {
            "status": self.state.status,
            "task": self.state.task,
            "current_step": self.state.current_step,
            "total_steps": len(self.state.sequence),
            "needs_clarification": self.needs_clarification(),
            "conversation_length": len(self.state.conversation)
        }
