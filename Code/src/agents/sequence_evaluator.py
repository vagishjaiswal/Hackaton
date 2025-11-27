"""
Sequence Evaluator Agent

This agent analyzes available agents and tools, then uses LLM to generate
an optimal execution sequence for completing user tasks.

Features:
- Discovers all available agents and tools
- Analyzes task requirements
- Generates execution sequence using LLM
- Provides reasoning for the sequence
- Identifies missing information/clarifications needed

Author: AI Assistant
Date: 2024-11-28
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.llm import LLMProviderFactory


logger = logging.getLogger(__name__)


class SequenceEvaluatorAgent(BaseAgent):
    """
    Agent that evaluates and generates optimal execution sequences.
    
    This agent:
    1. Discovers available agents and tools
    2. Analyzes user task/goal
    3. Uses LLM to generate execution sequence
    4. Identifies clarifications needed
    5. Provides reasoning for decisions
    
    Example:
        ```python
        evaluator = SequenceEvaluatorAgent()
        
        # Register available agents and tools
        evaluator.register_available_agent("DataAnalyst", "Analyzes CSV data...")
        evaluator.register_available_tool("CSVLoader", "Loads CSV files...")
        
        # Get sequence for a task
        result = await evaluator.evaluate_sequence(
            task="Analyze sales data and generate report"
        )
        ```
    """
    
    def __init__(
        self,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2",
        **kwargs
    ):
        """
        Initialize Sequence Evaluator Agent.
        
        Args:
            llm_provider: LLM provider to use
            llm_model: Model name
            **kwargs: Additional arguments
        """
        system_prompt = """You are a workflow sequence evaluator. Your role is to:

1. Analyze user tasks and break them down into steps
2. Match steps to available agents and tools
3. Generate optimal execution sequences
4. Identify missing information or clarifications needed
5. Provide clear reasoning for your decisions

Given a task and list of available agents/tools, you must:
- Think step-by-step about what needs to be done
- Select appropriate agents/tools for each step
- Arrange them in correct execution order
- Identify any missing information from the user
- Return structured JSON output

Always be thorough and consider edge cases."""
        
        super().__init__(
            name="SequenceEvaluator",
            role="coordinator",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            llm_model=llm_model,
            **kwargs
        )
        
        # Storage for available agents and tools
        self.available_agents: Dict[str, str] = {}
        self.available_tools: Dict[str, str] = {}
        
        self.logger.info("Sequence Evaluator Agent initialized")
    
    def register_available_agent(self, agent_name: str, description: str) -> None:
        """
        Register an available agent.
        
        Args:
            agent_name: Name of the agent
            description: What the agent does
            
        Example:
            ```python
            evaluator.register_available_agent(
                "DataAnalyst", 
                "Analyzes CSV data and provides insights"
            )
            ```
        """
        self.available_agents[agent_name] = description
        self.logger.debug(f"Registered agent: {agent_name}")
    
    def register_available_tool(self, tool_name: str, description: str) -> None:
        """
        Register an available tool.
        
        Args:
            tool_name: Name of the tool
            description: What the tool does
            
        Example:
            ```python
            evaluator.register_available_tool(
                "CSVLoader",
                "Loads and validates CSV files"
            )
            ```
        """
        self.available_tools[tool_name] = description
        self.logger.debug(f"Registered tool: {tool_name}")
    
    def get_available_resources(self) -> Dict[str, Any]:
        """
        Get all available agents and tools.
        
        Returns:
            Dictionary with agents and tools
        """
        return {
            "agents": self.available_agents,
            "tools": self.available_tools,
            "total_agents": len(self.available_agents),
            "total_tools": len(self.available_tools)
        }
    
    async def evaluate_sequence(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate and generate execution sequence for a task.
        
        Args:
            task: User task description
            context: Optional context (files, data, etc.)
            
        Returns:
            Dictionary containing:
            - sequence: List of steps with agent/tool assignments
            - clarifications: List of questions for user
            - reasoning: Explanation of the sequence
            - confidence: Confidence score (0-1)
            - can_execute: Whether we can proceed
            
        Example:
            ```python
            result = await evaluator.evaluate_sequence(
                task="Analyze sales data from Q4",
                context={"has_csv_file": True}
            )
            
            if result["clarifications"]:
                # Ask user for clarifications
                pass
            else:
                # Execute the sequence
                sequence = result["sequence"]
            ```
        """
        try:
            self.logger.info(f"Evaluating sequence for task: {task}")
            
            # Build prompt for LLM
            prompt = self._build_evaluation_prompt(task, context)
            
            # Generate response
            self.add_to_history("user", prompt)
            response = await self._generate_response(prompt, use_history=False)
            self.add_to_history("assistant", response)
            
            # Parse response
            result = self._parse_llm_response(response)
            
            self.logger.info(
                f"Sequence generated: {len(result.get('sequence', []))} steps, "
                f"{len(result.get('clarifications', []))} clarifications needed"
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error evaluating sequence: {e}")
            return {
                "status": "error",
                "error": str(e),
                "sequence": [],
                "clarifications": [],
                "can_execute": False
            }
    
    def _build_evaluation_prompt(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build prompt for LLM to evaluate sequence.
        
        Args:
            task: User task
            context: Optional context
            
        Returns:
            Formatted prompt
        """
        # Format available resources
        agents_list = "\n".join([
            f"- {name}: {desc}"
            for name, desc in self.available_agents.items()
        ])
        
        tools_list = "\n".join([
            f"- {name}: {desc}"
            for name, desc in self.available_tools.items()
        ])
        
        context_str = ""
        if context:
            context_str = f"\nContext:\n{json.dumps(context, indent=2)}\n"
        
        prompt = f"""Task: {task}
{context_str}
Available Agents:
{agents_list if agents_list else "None"}

Available Tools:
{tools_list if tools_list else "None"}

Please analyze this task and generate an execution sequence. Return ONLY a JSON object with this structure:

{{
  "sequence": [
    {{
      "step_number": 1,
      "step_name": "descriptive_name",
      "agent_or_tool": "AgentName or ToolName",
      "action": "what this step does",
      "inputs": {{"key": "value"}},
      "outputs": ["what this produces"]
    }}
  ],
  "clarifications": [
    {{
      "question": "what do you need to know?",
      "field": "field_name",
      "required": true/false,
      "options": ["option1", "option2"] or null
    }}
  ],
  "reasoning": "explanation of why this sequence makes sense",
  "confidence": 0.0-1.0,
  "can_execute": true/false,
  "missing_capabilities": ["what we can't do"] or []
}}

Important:
1. Only use agents/tools from the available lists above
2. Arrange steps in logical execution order
3. Identify ALL information you need from the user
4. If task is unclear or impossible, say so in clarifications
5. Think step-by-step through the workflow

Return ONLY the JSON object, no additional text."""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.
        
        Args:
            response: LLM response string
            
        Returns:
            Parsed dictionary
        """
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["sequence", "clarifications", "can_execute"]
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = [] if field != "can_execute" else False
            
            # Add status
            parsed["status"] = "success"
            
            return parsed
        
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            return {
                "status": "error",
                "error": f"Failed to parse LLM response: {str(e)}",
                "sequence": [],
                "clarifications": [
                    {
                        "question": "Could you rephrase your request more clearly?",
                        "field": "task",
                        "required": True
                    }
                ],
                "can_execute": False
            }
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return {
                "status": "error",
                "error": str(e),
                "sequence": [],
                "clarifications": [],
                "can_execute": False
            }
    
    async def execute(self, task: str, **kwargs) -> str:
        """
        Execute sequence evaluation (simplified interface).
        
        Args:
            task: Task description
            **kwargs: Additional arguments
            
        Returns:
            JSON string with evaluation result
        """
        context = kwargs.get("context")
        result = await self.evaluate_sequence(task, context)
        return json.dumps(result, indent=2)
    
    def validate_sequence(self, sequence: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate a generated sequence.
        
        Args:
            sequence: List of sequence steps
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not sequence:
            errors.append("Sequence is empty")
            return False, errors
        
        # Check each step
        for i, step in enumerate(sequence):
            step_num = i + 1
            
            # Check required fields
            required = ["step_number", "step_name", "agent_or_tool", "action"]
            for field in required:
                if field not in step:
                    errors.append(f"Step {step_num} missing '{field}'")
            
            # Check agent/tool exists
            agent_or_tool = step.get("agent_or_tool", "")
            if agent_or_tool not in self.available_agents and \
               agent_or_tool not in self.available_tools:
                errors.append(
                    f"Step {step_num} uses unknown agent/tool: {agent_or_tool}"
                )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SequenceEvaluatorAgent("
            f"agents={len(self.available_agents)}, "
            f"tools={len(self.available_tools)})"
        )
