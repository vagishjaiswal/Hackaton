"""
CSV Filter Agent - Usage Examples

This script demonstrates how to use the CSV Filter Agent to filter CSV files
and return results in JSON format.

Author: AI Assistant
Date: 2024-11-27
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.csv_filter_agent import CSVFilterAgent, filter_csv


def example_1_basic_usage():
    """Example 1: Basic usage with dictionary input"""
    print("\n" + "="*80)
    print("Example 1: Basic Usage with Dictionary Input")
    print("="*80)
    
    # Initialize the agent
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    # Create input as dictionary
    input_data = {
        "csv_file_name": "sample-csv.csv",
        "filtered_column_name": "Generate",
        "value": True
    }
    
    print("\nInput:")
    print(json.dumps(input_data, indent=2))
    
    # Process the request
    result = agent.process(input_data)
    
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    
    return result


def example_2_json_string_input():
    """Example 2: Using JSON string as input"""
    print("\n" + "="*80)
    print("Example 2: JSON String Input")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    # Create input as JSON string
    input_json = '''
    {
        "csv_file_name": "sample-csv.csv",
        "filtered_column_name": "Generate",
        "value": true
    }
    '''
    
    print("\nInput (JSON string):")
    print(input_json)
    
    # Process with JSON string
    result = agent.process(input_json)
    
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    
    return result


def example_3_filter_by_false():
    """Example 3: Filter rows where Generate is FALSE"""
    print("\n" + "="*80)
    print("Example 3: Filter by FALSE Value")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    input_data = {
        "csv_file_name": "sample-csv.csv",
        "filtered_column_name": "Generate",
        "value": False
    }
    
    print("\nInput:")
    print(json.dumps(input_data, indent=2))
    
    result = agent.process(input_data)
    
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    print(f"\nFound {len(result)} rows with Generate=False")
    
    return result


def example_4_filter_by_string():
    """Example 4: Filter by string value (Focus-Area)"""
    print("\n" + "="*80)
    print("Example 4: Filter by String Value")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    input_data = {
        "csv_file_name": "sample-csv.csv",
        "filtered_column_name": "Focus-Area",
        "value": "Azure"
    }
    
    print("\nInput:")
    print(json.dumps(input_data, indent=2))
    
    result = agent.process(input_data)
    
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    
    return result


def example_5_filter_by_number():
    """Example 5: Filter by numeric value (Count)"""
    print("\n" + "="*80)
    print("Example 5: Filter by Numeric Value")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    input_data = {
        "csv_file_name": "sample-csv.csv",
        "filtered_column_name": "Count",
        "value": 0
    }
    
    print("\nInput:")
    print(json.dumps(input_data, indent=2))
    
    result = agent.process(input_data)
    
    print("\nOutput (showing first 3 rows):")
    print(json.dumps(result[:3], indent=2))
    print(f"\n... Total {len(result)} rows with Count=0")
    
    return result


def example_6_get_json_string():
    """Example 6: Get result as JSON string"""
    print("\n" + "="*80)
    print("Example 6: Get Result as JSON String")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    input_data = {
        "csv_file_name": "sample-csv.csv",
        "filtered_column_name": "Generate",
        "value": True
    }
    
    # Get result as JSON string
    json_string = agent.process_to_json_string(input_data)
    
    print("\nOutput (JSON string):")
    print(json_string)
    
    return json_string


def example_7_preview_csv():
    """Example 7: Preview CSV file"""
    print("\n" + "="*80)
    print("Example 7: Preview CSV File")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    preview = agent.preview_csv("sample-csv.csv", n_rows=3)
    
    print("\nCSV Preview:")
    print(json.dumps(preview, indent=2))
    
    return preview


def example_8_get_headers():
    """Example 8: Get CSV headers"""
    print("\n" + "="*80)
    print("Example 8: Get CSV Headers")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    headers = agent.get_headers("sample-csv.csv")
    
    print("\nHeaders:")
    print(json.dumps(headers, indent=2))
    
    return headers


def example_9_convenience_function():
    """Example 9: Using the convenience function"""
    print("\n" + "="*80)
    print("Example 9: Using Convenience Function")
    print("="*80)
    
    # Quick one-liner filtering
    result = filter_csv(
        csv_file_name="sample-csv.csv",
        filtered_column_name="Generate",
        value=True,
        data_dir="Code/data/input"
    )
    
    print("\nFiltered Results:")
    print(json.dumps(result, indent=2))
    
    return result


def example_10_error_handling():
    """Example 10: Error handling"""
    print("\n" + "="*80)
    print("Example 10: Error Handling Examples")
    print("="*80)
    
    agent = CSVFilterAgent(data_dir="Code/data/input")
    
    # Test 1: Invalid column name
    print("\n--- Test 1: Invalid Column Name ---")
    try:
        result = agent.process({
            "csv_file_name": "sample-csv.csv",
            "filtered_column_name": "InvalidColumn",
            "value": True
        })
    except KeyError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Test 2: Missing file
    print("\n--- Test 2: Missing File ---")
    try:
        result = agent.process({
            "csv_file_name": "nonexistent.csv",
            "filtered_column_name": "Generate",
            "value": True
        })
    except FileNotFoundError as e:
        print(f"✓ Caught expected error: File not found")
    
    # Test 3: Missing required fields
    print("\n--- Test 3: Missing Required Fields ---")
    try:
        result = agent.process({
            "csv_file_name": "sample-csv.csv"
            # Missing filtered_column_name and value
        })
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("CSV FILTER AGENT - USAGE EXAMPLES")
    print("="*80)
    
    try:
        # Run examples
        example_1_basic_usage()
        example_2_json_string_input()
        example_3_filter_by_false()
        example_4_filter_by_string()
        example_5_filter_by_number()
        example_6_get_json_string()
        example_7_preview_csv()
        example_8_get_headers()
        example_9_convenience_function()
        example_10_error_handling()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
