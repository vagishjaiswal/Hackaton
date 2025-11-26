"""
LangGraph Interview Question Generation Workflow

This module implements a LangGraph-based workflow for generating interview questions
using a multi-step agentic approach.

Features:
- Multi-step workflow using LangGraph
- State management for user profiles and generated questions
- Tool integration for CSV data retrieval
- LLM-based question generation
- Error handling and validation

Usage:
    from langgraph_interview_workflow import create_interview_workflow
    
    workflow = create_interview_workflow(
        llm_provider="ollama",
        llm_model="llama3.2"
    )
    
    result = workflow.invoke({
        "user_id": 1,
        "csv_file": "test-agent.csv",
        "data_dir": "../../data/input",
        "num_questions": 5
    })

Author: AI Assistant
Date: 2024-11-27
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langgraph.graph import StateGraph, END
from src.agents.csv_filter_agent import CSVFilterAgent
from src.llm.llm_provider_factory import LLMProviderFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# State Definition
# ============================================================================

@dataclass
class InterviewWorkflowState:
    """State object for the interview workflow"""
    
    # Input parameters
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    csv_file: str = "test-agent.csv"
    data_dir: str = "../../data/input"
    num_questions: int = 5
    
    # Workflow state
    user_profile: Optional[Dict[str, Any]] = None
    csv_data: Optional[List[Dict[str, Any]]] = None
    prompt: Optional[str] = None
    raw_response: Optional[str] = None
    interview_questions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status tracking
    status: str = "initialized"
    error: Optional[str] = None
    step_count: int = 0
    
    def __dict__(self):
        """Convert to dictionary for LangGraph"""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "csv_file": self.csv_file,
            "data_dir": self.data_dir,
            "num_questions": self.num_questions,
            "user_profile": self.user_profile,
            "csv_data": self.csv_data,
            "prompt": self.prompt,
            "raw_response": self.raw_response,
            "interview_questions": self.interview_questions,
            "status": self.status,
            "error": self.error,
            "step_count": self.step_count,
        }


# ============================================================================
# Workflow Nodes
# ============================================================================

def fetch_user_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Fetch user profile from CSV
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with user profile
    """
    logger.info("Step 1: Fetching user profile...")
    
    try:
        user_id = state.get("user_id")
        user_name = state.get("user_name")
        csv_file = state.get("csv_file")
        data_dir = state.get("data_dir")
        
        # Validate input
        if not user_id and not user_name:
            raise ValueError("Either user_id or user_name must be provided")
        
        # Initialize CSV filter agent
        agent = CSVFilterAgent(data_dir=data_dir)
        
        # Fetch user data
        if user_id:
            logger.info(f"Fetching user by ID: {user_id}")
            csv_data = agent.process({
                "csv_file_name": csv_file,
                "filtered_column_name": "user_id",
                "value": user_id
            })
        else:
            logger.info(f"Fetching user by name: {user_name}")
            csv_data = agent.process({
                "csv_file_name": csv_file,
                "filtered_column_name": "name",
                "value": user_name
            })
        
        # Validate result
        if not csv_data or len(csv_data) == 0:
            raise ValueError(f"User not found: ID={user_id}, Name={user_name}")
        
        user_profile = csv_data[0]
        
        logger.info(f"✓ Found user: {user_profile.get('name', 'Unknown')}")
        
        return {
            **state,
            "user_profile": user_profile,
            "csv_data": csv_data,
            "status": "user_fetched",
            "step_count": state.get("step_count", 0) + 1,
        }
    
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        return {
            **state,
            "status": "error",
            "error": str(e),
            "step_count": state.get("step_count", 0) + 1,
        }


def validate_user_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Validate user profile and extract relevant information
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with validated profile
    """
    logger.info("Step 2: Validating user profile...")
    
    try:
        user_profile = state.get("user_profile")
        
        if not user_profile:
            raise ValueError("No user profile found in state")
        
        # Extract key fields
        required_fields = ["name", "job_role", "experience_years"]
        extracted = {}
        
        for field in required_fields:
            if field in user_profile:
                extracted[field] = user_profile[field]
            else:
                logger.warning(f"Missing field: {field}")
        
        # Extract optional fields
        optional_fields = ["skills", "education", "certifications"]
        for field in optional_fields:
            if field in user_profile:
                extracted[field] = user_profile[field]
        
        logger.info(f"✓ Profile validated: {extracted.get('name')}")
        
        return {
            **state,
            "user_profile": {**user_profile, **extracted},
            "status": "profile_validated",
            "step_count": state.get("step_count", 0) + 1,
        }
    
    except Exception as e:
        logger.error(f"Error validating profile: {e}")
        return {
            **state,
            "status": "error",
            "error": str(e),
            "step_count": state.get("step_count", 0) + 1,
        }


def build_prompt(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Build the prompt for question generation
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with generated prompt
    """
    logger.info("Step 3: Building question generation prompt...")
    
    try:
        user_profile = state.get("user_profile")
        num_questions = state.get("num_questions", 5)
        
        if not user_profile:
            raise ValueError("User profile required for prompt building")
        
        # Build prompt
        name = user_profile.get("name", "Unknown")
        role = user_profile.get("job_role", "Unknown")
        skills = user_profile.get("skills", "")
        experience = user_profile.get("experience_years", 0)
        
        prompt = f"""Generate {num_questions} interview questions for the following candidate:

Candidate Name: {name}
Job Role: {role}
Skills: {skills}
Years of Experience: {experience}

Generate questions that:
1. Are relevant to their skills and experience level
2. Cover different aspects of their expertise
3. Include a mix of technical, behavioral, and problem-solving questions
4. Are appropriate for their experience level ({experience} years)

Return ONLY a JSON object with this exact structure:
{{
  "questions": [
    {{
      "question": "question text",
      "category": "technical|behavioral|problem-solving",
      "difficulty": "junior|mid|senior",
      "rationale": "why this question is asked"
    }}
  ]
}}

No additional text, only valid JSON."""
        
        logger.info(f"✓ Prompt built for {name}")
        
        return {
            **state,
            "prompt": prompt,
            "status": "prompt_ready",
            "step_count": state.get("step_count", 0) + 1,
        }
    
    except Exception as e:
        logger.error(f"Error building prompt: {e}")
        return {
            **state,
            "status": "error",
            "error": str(e),
            "step_count": state.get("step_count", 0) + 1,
        }


def generate_questions(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 4: Generate interview questions using LLM
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with generated questions
    """
    logger.info("Step 4: Generating interview questions with LLM...")
    
    try:
        prompt = state.get("prompt")
        llm_provider = state.get("llm_provider", "ollama")
        llm_model = state.get("llm_model", "llama3.2")
        
        if not prompt:
            raise ValueError("Prompt required for question generation")
        
        # Initialize LLM using factory
        factory = LLMProviderFactory()
        llm = factory.create(llm_provider, llm_model)
        
        logger.info(f"Using LLM: {llm_provider}/{llm_model}")
        
        # Generate questions asynchronously
        response = asyncio.run(llm.generate(prompt))
        
        logger.info("✓ LLM response received")
        
        return {
            **state,
            "raw_response": response,
            "status": "questions_generated",
            "step_count": state.get("step_count", 0) + 1,
        }
    
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return {
            **state,
            "status": "error",
            "error": str(e),
            "step_count": state.get("step_count", 0) + 1,
        }


def parse_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 5: Parse and validate LLM response
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with parsed questions
    """
    logger.info("Step 5: Parsing LLM response...")
    
    try:
        raw_response = state.get("raw_response")
        
        if not raw_response:
            raise ValueError("No LLM response to parse")
        
        # Extract JSON from response
        # Try to find JSON in the response
        json_start = raw_response.find('{')
        json_end = raw_response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in LLM response")
        
        json_str = raw_response[json_start:json_end]
        parsed = json.loads(json_str)
        
        questions = parsed.get("questions", [])
        
        if not questions:
            raise ValueError("No questions found in parsed response")
        
        logger.info(f"✓ Parsed {len(questions)} questions")
        
        return {
            **state,
            "interview_questions": questions,
            "status": "questions_parsed",
            "step_count": state.get("step_count", 0) + 1,
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return {
            **state,
            "status": "error",
            "error": f"Failed to parse LLM response: {str(e)}",
            "step_count": state.get("step_count", 0) + 1,
        }
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        return {
            **state,
            "status": "error",
            "error": str(e),
            "step_count": state.get("step_count", 0) + 1,
        }


def format_output(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 6: Format the final output
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with formatted output
    """
    logger.info("Step 6: Formatting output...")
    
    try:
        status = state.get("status")
        error = state.get("error")
        user_profile = state.get("user_profile")
        interview_questions = state.get("interview_questions", [])
        
        if error:
            final_output = {
                "status": "error",
                "error": error,
                "user_profile": None,
                "interview_questions": []
            }
        else:
            final_output = {
                "status": "success",
                "user_profile": user_profile,
                "interview_questions": interview_questions,
                "metadata": {
                    "total_questions": len(interview_questions),
                    "user_name": user_profile.get("name") if user_profile else None,
                    "job_role": user_profile.get("job_role") if user_profile else None,
                    "steps_completed": state.get("step_count", 0)
                }
            }
        
        logger.info(f"✓ Output formatted: status={final_output['status']}")
        
        return {
            **state,
            "status": "completed",
            "step_count": state.get("step_count", 0) + 1,
            "final_output": final_output,
        }
    
    except Exception as e:
        logger.error(f"Error formatting output: {e}")
        return {
            **state,
            "status": "error",
            "error": str(e),
            "step_count": state.get("step_count", 0) + 1,
        }


# ============================================================================
# Conditional Routing
# ============================================================================

def should_continue(state: Dict[str, Any]) -> str:
    """
    Determine if workflow should continue or end based on errors
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name or END
    """
    status = state.get("status")
    
    if status == "error":
        return "format_output"  # Skip to formatting on error
    
    return "continue"


# ============================================================================
# Workflow Creation
# ============================================================================

def create_interview_workflow(
    llm_provider: str = "ollama",
    llm_model: str = "llama3.2"
):
    """
    Create and compile the interview question generation workflow
    
    Args:
        llm_provider: LLM provider name (ollama, openai, etc.)
        llm_model: LLM model name
        
    Returns:
        Compiled LangGraph workflow
    """
    logger.info(f"Creating interview workflow with {llm_provider}/{llm_model}")
    
    # Create workflow graph
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("fetch_profile", fetch_user_profile)
    workflow.add_node("validate_profile", validate_user_profile)
    workflow.add_node("build_prompt", build_prompt)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("parse_response", parse_response)
    workflow.add_node("format_output", format_output)
    
    # Set entry point
    workflow.set_entry_point("fetch_profile")
    
    # Add edges
    workflow.add_edge("fetch_profile", "validate_profile")
    workflow.add_edge("validate_profile", "build_prompt")
    workflow.add_edge("build_prompt", "generate_questions")
    workflow.add_edge("generate_questions", "parse_response")
    workflow.add_edge("parse_response", "format_output")
    
    # Add end
    workflow.add_edge("format_output", END)
    
    # Compile workflow
    compiled = workflow.compile()
    
    logger.info("✓ Workflow compiled successfully")
    
    return compiled


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Run example workflow"""
    print("\n" + "="*80)
    print("LANGGRAPH INTERVIEW QUESTION GENERATION WORKFLOW")
    print("="*80)
    
    try:
        # Create workflow
        workflow = create_interview_workflow(
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        
        # Initial state
        initial_state = {
            "user_id": 1,
            "csv_file": "test-agent.csv",
            "data_dir": "../../data/input",
            "num_questions": 3,
            "llm_provider": "ollama",
            "llm_model": "llama3.2",
        }
        
        print("\n[INPUT] Initial State:")
        print(json.dumps({k: v for k, v in initial_state.items() if k not in ["csv_file", "data_dir"]}, indent=2))
        
        # Run workflow
        print("\n[WORKFLOW] Executing workflow...")
        result = workflow.invoke(initial_state)
        
        # Output result
        if result.get("final_output"):
            output = result["final_output"]
            print("\n[OUTPUT] Final Result:")
            print(json.dumps(output, indent=2, default=str))
        else:
            print("\n[ERROR] No output produced")
            print(f"Status: {result.get('status')}")
            print(f"Error: {result.get('error')}")
    
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
