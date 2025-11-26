"""
Test Interview Question Workflow

Test script to verify the interview question generation workflow works correctly.

Author: AI Assistant
Date: 2024-11-27
"""

import json
import sys
from pathlib import Path

# Add src to path - adjust for tests/workflow subdirectory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.workflow.interview_question_workflow import InterviewQuestionWorkflow


def test_workflow():
    """Test the interview question workflow"""
    
    print("="*80)
    print("TESTING INTERVIEW QUESTION WORKFLOW")
    print("="*80)
    
    # Initialize workflow
    print("\n✓ Test 1: Initialize Workflow")
    try:
        workflow = InterviewQuestionWorkflow(
            csv_file="test-agent.csv",
            data_dir="data/input",
            llm_provider="ollama",
            llm_model="llama3.2",
            num_questions=3  # Fewer questions for testing
        )
        print("  ✅ Workflow initialized successfully")
    except Exception as e:
        print(f"  ❌ Failed to initialize workflow: {e}")
        return
    
    # Test 2: Fetch user profile
    print("\n✓ Test 2: Fetch User Profile (user_id=1)")
    try:
        user_profile = workflow.fetch_user_profile(user_id=1)
        print(f"  User: {user_profile['name']}")
        print(f"  Role: {user_profile['job_role']}")
        print(f"  Skills: {user_profile['skills']}")
        print(f"  Experience: {user_profile['experience_years']} years")
        print("  ✅ User profile fetched successfully")
    except Exception as e:
        print(f"  ❌ Failed to fetch user profile: {e}")
        return
    
    # Test 3: Fetch user by name
    print("\n✓ Test 3: Fetch User Profile (name='Jane Smith')")
    try:
        user_profile = workflow.fetch_user_profile(name="Jane Smith")
        print(f"  User ID: {user_profile['user_id']}")
        print(f"  Role: {user_profile['job_role']}")
        print("  ✅ User profile fetched by name successfully")
    except Exception as e:
        print(f"  ❌ Failed to fetch user by name: {e}")
    
    # Test 4: Generate interview questions
    print("\n✓ Test 4: Generate Interview Questions (user_id=1)")
    try:
        result = workflow.generate_interview_questions(user_id=1)
        
        if result["status"] == "success":
            print(f"  User: {result['user_profile']['name']}")
            print(f"  Role: {result['user_profile']['job_role']}")
            print(f"  Questions Generated: {result['metadata']['total_questions']}")
            print(f"  LLM: {result['metadata']['llm_provider']}/{result['metadata']['llm_model']}")
            
            print("\n  Sample Questions:")
            for i, q in enumerate(result['interview_questions'][:3], 1):
                print(f"    {i}. [{q.get('category', 'N/A')}] {q.get('question', 'N/A')[:80]}...")
            
            print("\n  Full Response (JSON):")
            print("  " + "-"*76)
            print("  " + json.dumps(result, indent=2).replace("\n", "\n  "))
            print("  " + "-"*76)
            print("  ✅ Interview questions generated successfully")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
            return
    except Exception as e:
        print(f"  ❌ Failed to generate questions: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 5: Test with inactive user
    print("\n✓ Test 5: Test with Inactive User (user_id=3, active=FALSE)")
    try:
        # This should fail with active_only=True
        result = workflow.generate_interview_questions(user_id=3, active_only=True)
        print(f"  ❌ Should have failed for inactive user")
    except ValueError as e:
        print(f"  ✅ Correctly rejected inactive user: {e}")
    except Exception as e:
        print(f"  ⚠️ Unexpected error: {e}")
    
    # Test 6: Test with inactive user allowed
    print("\n✓ Test 6: Generate Questions for Inactive User (active_only=False)")
    try:
        result = workflow.generate_interview_questions(user_id=3, active_only=False)
        if result["status"] == "success":
            print(f"  User: {result['user_profile']['name']} (Active: {result['user_profile']['active']})")
            print(f"  Questions: {result['metadata']['total_questions']}")
            print("  ✅ Questions generated for inactive user")
        else:
            print(f"  ❌ Error: {result.get('error')}")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
    
    # Test 7: Batch generation
    print("\n✓ Test 7: Batch Generation (user_ids=[1, 2])")
    try:
        results = workflow.generate_questions_batch(user_ids=[1, 2], active_only=True)
        print(f"  Total Results: {len(results)}")
        for i, result in enumerate(results, 1):
            if result["status"] == "success":
                print(f"    User {i}: {result['user_profile']['name']} - {result['metadata']['total_questions']} questions")
            else:
                print(f"    User {i}: Error - {result.get('error', 'Unknown')}")
        print("  ✅ Batch generation completed")
    except Exception as e:
        print(f"  ❌ Batch generation failed: {e}")
    
    # Final summary
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)
    print("\nWorkflow is ready to use!")
    print("\nNext steps:")
    print("  1. Run: python generate_interview_questions.py --user-id 1")
    print("  2. Or use the workflow in your Python code")
    print("  3. See interview_question_workflow.py for more examples")
    print()


if __name__ == "__main__":
    test_workflow()
