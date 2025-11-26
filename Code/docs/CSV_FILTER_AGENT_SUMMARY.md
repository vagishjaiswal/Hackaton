# CSV Filter Agent - Implementation Summary

## Overview

I've created a specialized agent that takes JSON input and filters CSV files based on column values. The agent returns matching rows as a JSON array with headers as keys.

## Files Created

### 1. Core Agent Implementation
**File**: `Code/src/agents/csv_filter_agent.py`
- Main agent class: `CSVFilterAgent`
- Processes JSON input and filters CSV files
- Returns results as JSON array
- Includes helper methods for headers, preview, etc.

### 2. Test Script
**File**: `Code/test_csv_filter_agent.py`
- Quick validation tests
- Tests boolean, string, and numeric filtering
- Verifies headers and preview functionality

### 3. Comprehensive Examples
**File**: `Code/example_csv_filter_agent.py`
- 10 detailed usage examples
- Covers all features and error handling
- Shows different input formats and use cases

### 4. Standalone CLI Tool
**File**: `Code/csv_filter_standalone.py`
- Command-line interface
- Can accept JSON input or individual arguments
- Supports file output
- Can be used as a module or CLI tool

### 5. Documentation
**File**: `Code/docs/csv_filter_agent_guide.md`
- Complete usage guide
- API reference
- Examples with sample data
- Error handling documentation

### 6. Example JSON Input
**File**: `Code/data/input/filter_input_example.json`
- Sample JSON input file
- Shows correct format

## Input Format

```json
{
  "csv_file_name": "sample-csv.csv",
  "filtered_column_name": "Generate",
  "value": true
}
```

## Output Format

```json
[
  {
    "Focus-Area": "SQL",
    "Color": "Dark Golden & Light yellow",
    "Background": "Black",
    "Generate": true,
    "Count": 0
  }
]
```

## Key Features

1. **Flexible Input**: Accepts dict or JSON string
2. **Type Handling**: Automatically handles boolean, string, and numeric values
3. **Header Mapping**: First row becomes keys in JSON objects
4. **Filtering**: Filters rows based on column value match
5. **Error Handling**: Clear error messages for common issues
6. **Multiple Interfaces**: Python API, convenience function, CLI tool

## Usage Examples

### Python API

```python
from src.agents.csv_filter_agent import CSVFilterAgent

# Initialize agent
agent = CSVFilterAgent(data_dir="data/input")

# Process request
input_data = {
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": True
}

result = agent.process(input_data)
print(json.dumps(result, indent=2))
```

### Convenience Function

```python
from src.agents.csv_filter_agent import filter_csv

result = filter_csv(
    csv_file_name="sample-csv.csv",
    filtered_column_name="Generate",
    value=True
)
```

### Command Line

```bash
# Using JSON file
python csv_filter_standalone.py --input filter_input_example.json --pretty

# Using arguments
python csv_filter_standalone.py --csv sample-csv.csv --column Generate --value true --pretty

# Save to file
python csv_filter_standalone.py --csv sample-csv.csv --column Generate --value true --output results.json
```

## Testing

### Quick Test
```bash
cd Code
python test_csv_filter_agent.py
```

### Comprehensive Examples
```bash
cd Code
python example_csv_filter_agent.py
```

### CLI Test
```bash
cd Code
python csv_filter_standalone.py --input data/input/filter_input_example.json --pretty
```

## Sample CSV Data

The implementation works with your `sample-csv.csv`:

```csv
Focus-Area,Color,Background,Generate,Count
Azure,White & Dark Blue,Black,FALSE,0
Java,White & Dark brown,Black,FALSE,0
SQL,Dark Golden & Light yellow,Black,TRUE,0
GenAI,White & Light Grey,Dark Blue,FALSE,0
DevOps,White & Light Grey,Dark Blue,FALSE,0
```

## Filter Examples

### Filter by Boolean (Generate=True)
**Input**:
```json
{
  "csv_file_name": "sample-csv.csv",
  "filtered_column_name": "Generate",
  "value": true
}
```

**Output**:
```json
[
  {
    "Focus-Area": "SQL",
    "Color": "Dark Golden & Light yellow",
    "Background": "Black",
    "Generate": true,
    "Count": 0
  }
]
```

### Filter by String (Focus-Area=Azure)
**Input**:
```json
{
  "csv_file_name": "sample-csv.csv",
  "filtered_column_name": "Focus-Area",
  "value": "Azure"
}
```

**Output**:
```json
[
  {
    "Focus-Area": "Azure",
    "Color": "White & Dark Blue",
    "Background": "Black",
    "Generate": false,
    "Count": 0
  }
]
```

### Filter by Number (Count=0)
**Input**:
```json
{
  "csv_file_name": "sample-csv.csv",
  "filtered_column_name": "Count",
  "value": 0
}
```

**Output**: All 5 rows (all have Count=0)

## Error Handling

The agent provides clear error messages:

1. **Missing File**: "CSV file not found: {path}"
2. **Invalid Column**: "Column '{name}' not found. Available columns: [...]"
3. **Missing Fields**: "Missing required fields: [...]"
4. **Invalid JSON**: "Invalid JSON input: {error}"

## Integration with Existing Code

The agent integrates seamlessly with your existing codebase:
- Uses the existing `CSVLoader` from `src.tools.csv_tools`
- Follows the same patterns as other agents
- Compatible with existing LLM providers
- Uses consistent logging

## Additional Features

1. **Get Headers**: `agent.get_headers("sample-csv.csv")`
2. **Preview CSV**: `agent.preview_csv("sample-csv.csv", n_rows=5)`
3. **JSON String Output**: `agent.process_to_json_string(input_data)`
4. **Dataframe Output**: `agent.process(input_data, output_format="dataframe")`

## Next Steps

You can now:
1. Run the tests to verify everything works
2. Use the agent in your existing workflow
3. Integrate with your LLM agents if needed
4. Extend the agent with additional filtering capabilities
5. Use the CLI tool for standalone operations

## Dependencies

No additional dependencies required. Uses existing project dependencies:
- pandas
- chardet
- Standard library (json, pathlib, logging, etc.)

---

**Author**: AI Assistant  
**Date**: 2024-11-27  
**Status**: Complete and Ready to Use
