#!/usr/bin/env python3
"""
Interview Question Generator - Standalone Script

Simple command-line tool to generate interview questions for users.

Usage:
    python generate_interview_questions.py --user-id 1
    python generate_interview_questions.py --name "John Doe"
    python generate_interview_questions.py --user-id 1 --questions 10
    python generate_interview_questions.py --batch --user-ids 1 2 3

Author: AI Assistant
Date: 2024-11-27
"""

import json
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from interview_question_workflow import InterviewQuestionWorkflow


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate interview questions based on user profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate questions for user ID 1
  python generate_interview_questions.py --user-id 1
  
  # Generate questions by name
  python generate_interview_questions.py --name "Jane Smith"
  
  # Generate 10 questions
  python generate_interview_questions.py --user-id 1 --questions 10
  
  # Batch generation for multiple users
  python generate_interview_questions.py --batch --user-ids 1 2 3 4
  
  # Save to file
  python generate_interview_questions.py --user-id 1 --output questions.json
  
  # Use specific LLM model
  python generate_interview_questions.py --user-id 1 --model llama3.2
        """
    )
    
    # User selection
    parser.add_argument(
        '--user-id', '-u',
        type=int,
        help='User ID to generate questions for'
    )
    parser.add_argument(
        '--name', '-n',
        help='User name to generate questions for'
    )
    
    # Batch processing
    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help='Batch mode: generate for multiple users'
    )
    parser.add_argument(
        '--user-ids',
        type=int,
        nargs='+',
        help='List of user IDs for batch processing'
    )
    
    # Configuration
    parser.add_argument(
        '--questions', '-q',
        type=int,
        default=5,
        help='Number of questions to generate (default: 5)'
    )
    parser.add_argument(
        '--csv-file',
        default='test-agent.csv',
        help='CSV file name (default: test-agent.csv)'
    )
    parser.add_argument(
        '--data-dir',
        default='../../data/input',
        help='Data directory (default: ../../data/input)'
    )
    parser.add_argument(
        '--provider',
        default='ollama',
        help='LLM provider (default: ollama)'
    )
    parser.add_argument(
        '--model',
        default='llama3.2',
        help='LLM model (default: llama3.2)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output file path (JSON)'
    )
    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        help='Pretty print JSON output'
    )
    parser.add_argument(
        '--include-inactive',
        action='store_true',
        help='Include inactive users'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.batch and not args.user_id and not args.name:
        parser.print_help()
        print("\nError: Must specify --user-id, --name, or --batch", file=sys.stderr)
        sys.exit(1)
    
    if args.batch and not args.user_ids:
        parser.print_help()
        print("\nError: --batch requires --user-ids", file=sys.stderr)
        sys.exit(1)
    
    # Initialize workflow
    print("Initializing workflow...", file=sys.stderr)
    workflow = InterviewQuestionWorkflow(
        csv_file=args.csv_file,
        data_dir=args.data_dir,
        llm_provider=args.provider,
        llm_model=args.model,
        num_questions=args.questions
    )
    
    # Generate questions
    try:
        if args.batch:
            # Batch processing
            print(f"Generating questions for {len(args.user_ids)} users...", file=sys.stderr)
            results = workflow.generate_questions_batch(
                user_ids=args.user_ids,
                active_only=not args.include_inactive
            )
            output_data = {
                "batch_results": results,
                "total_users": len(results),
                "successful": sum(1 for r in results if r["status"] == "success")
            }
        else:
            # Single user processing
            if args.user_id:
                print(f"Generating questions for user_id={args.user_id}...", file=sys.stderr)
                result = workflow.generate_interview_questions(
                    user_id=args.user_id,
                    active_only=not args.include_inactive
                )
            else:
                print(f"Generating questions for name='{args.name}'...", file=sys.stderr)
                result = workflow.generate_interview_questions(
                    name=args.name,
                    active_only=not args.include_inactive
                )
            
            output_data = result
        
        # Format output
        if args.pretty:
            output = json.dumps(output_data, indent=2, default=str)
        else:
            output = json.dumps(output_data, default=str)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"\n✓ Output written to: {args.output}", file=sys.stderr)
        else:
            print("\n" + output)
        
        # Print summary
        if args.batch:
            print(f"\n✓ Generated questions for {output_data['successful']}/{output_data['total_users']} users", file=sys.stderr)
        else:
            if output_data["status"] == "success":
                print(f"\n✓ Generated {output_data['metadata']['total_questions']} questions", file=sys.stderr)
            else:
                print(f"\n✗ Error: {output_data.get('error', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
