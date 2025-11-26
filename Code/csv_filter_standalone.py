#!/usr/bin/env python3
"""
CSV Filter Agent - Standalone Script

A command-line interface for the CSV Filter Agent.
Can be used as a standalone script or imported as a module.

Usage:
    # As command-line tool
    python csv_filter_standalone.py --input input.json
    python csv_filter_standalone.py --csv sample.csv --column Generate --value true
    
    # As Python module
    from csv_filter_standalone import filter_csv_file
    result = filter_csv_file("sample.csv", "Generate", True)

Author: AI Assistant
Date: 2024-11-27
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Union

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.csv_filter_agent import CSVFilterAgent


def filter_csv_file(
    csv_file_name: str,
    filtered_column_name: str,
    value: Any,
    data_dir: str = "data/input"
) -> List[Dict[str, Any]]:
    """
    Filter a CSV file and return matching rows.
    
    Args:
        csv_file_name: Name of the CSV file
        filtered_column_name: Column to filter by
        value: Value to match
        data_dir: Directory containing CSV files
        
    Returns:
        List of dictionaries with matching rows
        
    Example:
        >>> result = filter_csv_file("sample-csv.csv", "Generate", True)
        >>> print(json.dumps(result, indent=2))
    """
    agent = CSVFilterAgent(data_dir=data_dir)
    
    input_data = {
        "csv_file_name": csv_file_name,
        "filtered_column_name": filtered_column_name,
        "value": value
    }
    
    return agent.process(input_data)


def process_json_input(json_input: str, data_dir: str = "data/input") -> List[Dict[str, Any]]:
    """
    Process JSON input string and return filtered results.
    
    Args:
        json_input: JSON string or path to JSON file
        data_dir: Directory containing CSV files
        
    Returns:
        List of dictionaries with matching rows
        
    Example:
        >>> json_str = '{"csv_file_name": "sample.csv", "filtered_column_name": "Generate", "value": true}'
        >>> result = process_json_input(json_str)
    """
    # Check if input is a file path
    if Path(json_input).exists():
        with open(json_input, 'r') as f:
            json_input = f.read()
    
    # Parse JSON
    try:
        input_data = json.loads(json_input)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {e}")
    
    # Add data_dir if not in input
    agent = CSVFilterAgent(data_dir=data_dir)
    return agent.process(input_data)


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description="CSV Filter Agent - Filter CSV files by column values",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using JSON input file
  python csv_filter_standalone.py --input input.json
  
  # Using JSON string
  python csv_filter_standalone.py --input '{"csv_file_name": "sample.csv", "filtered_column_name": "Generate", "value": true}'
  
  # Using individual arguments
  python csv_filter_standalone.py --csv sample-csv.csv --column Generate --value true
  python csv_filter_standalone.py --csv sample-csv.csv --column Focus-Area --value Azure
  
  # Specify data directory
  python csv_filter_standalone.py --csv sample.csv --column Generate --value true --data-dir /path/to/data
  
  # Pretty print output
  python csv_filter_standalone.py --csv sample.csv --column Generate --value true --pretty
        """
    )
    
    # Input method 1: JSON input
    parser.add_argument(
        '--input', '-i',
        help='JSON input string or path to JSON file containing filter parameters'
    )
    
    # Input method 2: Individual arguments
    parser.add_argument(
        '--csv', '-c',
        help='Name of the CSV file'
    )
    parser.add_argument(
        '--column', '-col',
        help='Column name to filter by'
    )
    parser.add_argument(
        '--value', '-v',
        help='Value to match in the column'
    )
    
    # Common arguments
    parser.add_argument(
        '--data-dir', '-d',
        default='data/input',
        help='Directory containing CSV files (default: data/input)'
    )
    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        help='Pretty print JSON output'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (if not specified, prints to stdout)'
    )
    
    args = parser.parse_args()
    
    # Determine which input method to use
    if args.input:
        # Method 1: JSON input
        try:
            result = process_json_input(args.input, data_dir=args.data_dir)
        except Exception as e:
            print(f"Error processing JSON input: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.csv and args.column and args.value is not None:
        # Method 2: Individual arguments
        try:
            # Convert value to appropriate type
            value = args.value
            
            # Try to convert to boolean
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            else:
                # Try to convert to number
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    # Keep as string
                    pass
            
            result = filter_csv_file(
                csv_file_name=args.csv,
                filtered_column_name=args.column,
                value=value,
                data_dir=args.data_dir
            )
        except Exception as e:
            print(f"Error filtering CSV: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\nError: You must provide either --input or all of (--csv, --column, --value)", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.pretty:
        output = json.dumps(result, indent=2, default=str)
    else:
        output = json.dumps(result, default=str)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Output written to: {args.output}")
    else:
        print(output)
    
    # Print summary to stderr
    print(f"\nProcessed: {len(result)} matching row(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
