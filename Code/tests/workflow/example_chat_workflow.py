"""
Example: Chat-Based Workflow with Sequence Evaluator

This example demonstrates how to use the chat-based workflow
with automatic sequence generation and execution.

Run with:
    python tests/workflow/example_chat_workflow.py

Author: AI Assistant
Date: 2024-11-28
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.workflow.chat_workflow import ChatBasedWorkflow


async def simple_example():
    """Simple example with no clarifications needed."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Task (No Clarifications)")
    print("="*80 + "\n")
    
    # Create workflow
    workflow = ChatBasedWorkflow(
        llm_provider="openai",
        llm_model="gpt-5-nano",
        data_dir="data/input"
    )
    
    # User task
    task = "Answer this question: What is the capital of France?"
    print(f"USER: {task}\n")
    
    # Process
    response = await workflow.process_message(task)
    print(f"ASSISTANT: {response}\n")
    
    # Show final state
    state = workflow.get_state()
    print(f"\nFinal State: {json.dumps(state, indent=2)}")


async def clarification_example():
    """Example that requires clarifications."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Task Requiring Clarifications")
    print("="*80 + "\n")
    
    # Create workflow
    workflow = ChatBasedWorkflow(
        llm_provider="openai",
        llm_model="gpt-5-nano",
        data_dir="data/input"
    )
    
    # User provides vague task
    task = "Analyze some data for me"
    print(f"USER: {task}\n")
    
    response = await workflow.process_message(task)
    print(f"ASSISTANT: {response}\n")
    
    # Check if needs clarification
    if workflow.needs_clarification():
        print("\n[Workflow needs clarification]\n")
        
        # User provides clarifications
        clarifications = {
            "csv_file": "sample-csv.csv",
            "analysis_type": "summary statistics"
        }
        
        print(f"USER: Here's what you need:\n{json.dumps(clarifications, indent=2)}\n")
        
        response = await workflow.process_message(json.dumps(clarifications))
        print(f"ASSISTANT: {response}\n")
    
    # Show final state
    state = workflow.get_state()
    print(f"\nFinal State: {json.dumps(state, indent=2)}")


async def data_analysis_example():
    """Example: Data analysis workflow."""
    print("\n" + "="*80)
    print("EXAMPLE 3: CSV Data Analysis")
    print("="*80 + "\n")
    
    # Create workflow
    workflow = ChatBasedWorkflow(
        llm_provider="ollama",
        llm_model="llama3.2",
        data_dir="data/input"
    )
    
    # User task with context
    task = "Load the file sample-csv.csv and tell me how many rows it has"
    print(f"USER: {task}\n")
    
    response = await workflow.process_message(task)
    print(f"ASSISTANT: {response}\n")
    
    # If clarifications needed
    if workflow.needs_clarification():
        clarifications = workflow.get_clarifications()
        print(f"\n[Clarifications needed: {len(clarifications)}]\n")
        
        for c in clarifications:
            print(f"Q: {c['question']}")
            
            # Simulate user answer
            if c['field'] == 'csv_file':
                answer = "sample-csv.csv"
            else:
                answer = "yes"
            
            print(f"A: {answer}\n")
        
        # Provide answers
        answers = {c['field']: "sample-csv.csv" for c in clarifications}
        response = await workflow.process_message(json.dumps(answers))
        print(f"ASSISTANT: {response}\n")
    
    # Show state
    state = workflow.get_state()
    print(f"\nFinal State: {json.dumps(state, indent=2)}")


async def interactive_mode():
    """Interactive chat mode."""
    print("\n" + "="*80)
    print("INTERACTIVE CHAT MODE")
    print("="*80)
    print("\nType 'quit' to exit\n")
    
    # Create workflow
    workflow = ChatBasedWorkflow(
        llm_provider="ollama",
        llm_model="llama3.2",
        data_dir="data/input",
        verbose=False
    )
    
    while True:
        # Get user input
        try:
            user_input = input("\nYOU: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_input:
                continue
            
            # Process message
            print("\nASSISTANT: ", end="", flush=True)
            response = await workflow.process_message(user_input)
            print(response)
            
            # Show state
            if user_input.startswith("!state"):
                state = workflow.get_state()
                print(f"\nState: {json.dumps(state, indent=2)}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


async def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("CHAT-BASED WORKFLOW EXAMPLES")
    print("="*80)
    
    # Run examples
    await simple_example()
    
    print("\n" + "="*80)
    input("\nPress Enter to continue to next example...")
    
    await clarification_example()
    
    print("\n" + "="*80)
    input("\nPress Enter to continue to next example...")
    
    await data_analysis_example()
    
    print("\n" + "="*80)
    print("\nExamples completed!")
    
    # Ask if want interactive mode
    print("\nWould you like to try interactive mode? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice == 'y':
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
