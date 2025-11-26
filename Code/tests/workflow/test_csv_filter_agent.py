"""
Test CSV Filter Agent

Quick test to verify the CSV Filter Agent works correctly.

Author: AI Assistant  
Date: 2024-11-27
"""

import json
import sys
from pathlib import Path

# Add src to path - adjust for tests/workflow subdirectory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.csv_filter_agent import CSVFilterAgent


def test_csv_filter_agent():
    """Test the CSV Filter Agent with the sample CSV"""
    
    print("Testing CSV Filter Agent...")
    print("="*80)
    
    # Initialize agent
    agent = CSVFilterAgent(data_dir="data/input")
    
    # Test 1: Filter by Generate=True
    print("\n✓ Test 1: Filter rows where Generate=True")
    input_data = {
        "csv_file_name": "sample-csv.csv",
        "filtered_column_name": "Generate",
        "value": True
    }
    
    result = agent.process(input_data)
    print(f"  Input: {json.dumps(input_data)}")
    print(f"  Result: {json.dumps(result, indent=2)}")
    print(f"  ✅ Found {len(result)} matching row(s)")
    
    # Test 2: Filter by Generate=False  
    print("\n✓ Test 2: Filter rows where Generate=False")
    input_data["value"] = False
    
    result = agent.process(input_data)
    print(f"  Input: {json.dumps(input_data)}")
    print(f"  Result count: {len(result)} rows")
    print(f"  ✅ Found {len(result)} matching row(s)")
    
    # Test 3: Get headers
    print("\n✓ Test 3: Get CSV headers")
    headers = agent.get_headers("sample-csv.csv")
    print(f"  Headers: {headers}")
    print(f"  ✅ Found {len(headers)} columns")
    
    # Test 4: Preview CSV
    print("\n✓ Test 4: Preview CSV file")
    preview = agent.preview_csv("sample-csv.csv", n_rows=2)
    print(f"  Total rows: {preview['row_count']}")
    print(f"  Columns: {preview['columns']}")
    print(f"  Preview (first 2 rows): {json.dumps(preview['preview'], indent=2)}")
    print(f"  ✅ Preview successful")
    
    print("\n" + "="*80)
    print("✅ All tests passed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_csv_filter_agent()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
