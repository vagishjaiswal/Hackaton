"""
Test LangGraph Interview Workflow

Simple test to verify the workflow structure without waiting for LLM response.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path - adjust for tests/workflow subdirectory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.workflow.langgraph_interview_workflow import (
    create_interview_workflow,
    fetch_user_profile,
    validate_user_profile,
    build_prompt
)


def test_workflow_steps():
    """Test individual workflow steps"""
    print("\n" + "="*80)
    print("TESTING LANGGRAPH WORKFLOW STEPS")
    print("="*80)
    
    # Test Step 1: Fetch user profile
    print("\n[TEST 1] Fetch User Profile")
    state1 = {
        "user_id": 1,
        "csv_file": "test-agent.csv",
        "data_dir": "../../data/input",
        "step_count": 0,
    }
    
    try:
        result1 = fetch_user_profile(state1)
        if result1.get("status") == "user_fetched":
            print(f"  Status: {result1['status']}")
            print(f"  User: {result1['user_profile'].get('name')}")
            print(f"  Role: {result1['user_profile'].get('job_role')}")
            print("  [PASSED]")
        else:
            print(f"  [FAILED]: {result1.get('error')}")
            return
    except Exception as e:
        print(f"  [FAILED]: {e}")
        return
    
    # Test Step 2: Validate profile
    print("\n[TEST 2] Validate User Profile")
    try:
        result2 = validate_user_profile(result1)
        if result2.get("status") == "profile_validated":
            print(f"  Status: {result2['status']}")
            print(f"  User: {result2['user_profile'].get('name')}")
            print("  [PASSED]")
        else:
            print(f"  [FAILED]: {result2.get('error')}")
            return
    except Exception as e:
        print(f"  [FAILED]: {e}")
        return
    
    # Test Step 3: Build prompt
    print("\n[TEST 3] Build Question Prompt")
    result2["num_questions"] = 3
    try:
        result3 = build_prompt(result2)
        if result3.get("status") == "prompt_ready":
            print(f"  Status: {result3['status']}")
            print(f"  Prompt length: {len(result3['prompt'])} characters")
            print(f"  Preview: {result3['prompt'][:100]}...")
            print("  [PASSED]")
        else:
            print(f"  [FAILED]: {result3.get('error')}")
            return
    except Exception as e:
        print(f"  [FAILED]: {e}")
        return
    
    # Test Step 4: Create workflow
    print("\n[TEST 4] Create LangGraph Workflow")
    try:
        workflow = create_interview_workflow(
            llm_provider="ollama",
            llm_model="llama3.2"
        )
        print(f"  Workflow type: {type(workflow).__name__}")
        print("  [PASSED]")
    except Exception as e:
        print(f"  [FAILED]: {e}")
        return
    
    print("\n" + "="*80)
    print("[SUCCESS] ALL WORKFLOW STEP TESTS PASSED!")
    print("="*80)
    print("\nWorkflow structure verified. LLM generation step requires Ollama connection.")
    print("Run full workflow with: python langgraph_interview_workflow.py")


if __name__ == "__main__":
    test_workflow_steps()
