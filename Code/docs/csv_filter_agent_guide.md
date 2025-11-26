# CSV Filter Agent

A specialized agent for filtering CSV files based on column values and returning results in JSON format.

## Overview

The CSV Filter Agent provides a simple interface to:
- Load CSV files
- Filter rows based on a specific column and value
- Return matching rows as JSON array with headers as keys
- Handle boolean, numeric, and string comparisons

## Input Format

```json
{
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": true
}
```

### Required Fields

- `csv_file_name` (string): Name of the CSV file in the data directory
- `filtered_column_name` (string): Name of the column to filter by
- `value` (any): Value to match in the filtered column

## Output Format

Returns an array of JSON objects, where each object represents a row that matches the filter criteria:

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

## Installation

No additional dependencies required beyond the main project requirements.

## Usage

### Basic Usage

```python
from src.agents.csv_filter_agent import CSVFilterAgent

# Initialize the agent
agent = CSVFilterAgent(data_dir="data/input")

# Create input
input_data = {
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": True
}

# Process and get results
result = agent.process(input_data)
print(result)
```

### Using JSON String Input

```python
# Input as JSON string
input_json = '''
{
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": true
}
'''

result = agent.process(input_json)
```

### Get Result as JSON String

```python
json_string = agent.process_to_json_string(input_data)
print(json_string)
```

### Convenience Function

```python
from src.agents.csv_filter_agent import filter_csv

# Quick one-liner
result = filter_csv(
    csv_file_name="sample-csv.csv",
    filtered_column_name="Generate",
    value=True,
    data_dir="data/input"
)
```

## Additional Features

### Get CSV Headers

```python
headers = agent.get_headers("sample-csv.csv")
print(headers)
# Output: ['Focus-Area', 'Color', 'Background', 'Generate', 'Count']
```

### Preview CSV File

```python
preview = agent.preview_csv("sample-csv.csv", n_rows=5)
print(preview)
# Returns metadata and first 5 rows
```

## Supported Filter Types

The agent automatically handles different data types:

### Boolean Values
```python
{"filtered_column_name": "Generate", "value": True}
{"filtered_column_name": "Generate", "value": False}
```

### String Values
```python
{"filtered_column_name": "Focus-Area", "value": "Azure"}
{"filtered_column_name": "Color", "value": "White & Dark Blue"}
```

### Numeric Values
```python
{"filtered_column_name": "Count", "value": 0}
{"filtered_column_name": "Count", "value": 5}
```

## Example with Sample CSV

Given `sample-csv.csv`:
```csv
Focus-Area,Color,Background,Generate,Count
Azure,White & Dark Blue,Black,FALSE,0
Java,White & Dark brown,Black,FALSE,0
SQL,Dark Golden & Light yellow,Black,TRUE,0
GenAI,White & Light Grey,Dark Blue,FALSE,0
DevOps,White & Light Grey,Dark Blue,FALSE,0
```

### Filter for Generate=True
```python
input_data = {
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": True
}
result = agent.process(input_data)
```

Output:
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

## Error Handling

The agent provides clear error messages for common issues:

### Missing File
```python
# FileNotFoundError with helpful message
result = agent.process({
    "csv_file_name": "nonexistent.csv",
    "filtered_column_name": "Generate",
    "value": True
})
```

### Invalid Column
```python
# KeyError with list of available columns
result = agent.process({
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "InvalidColumn",
    "value": True
})
```

### Missing Required Fields
```python
# ValueError with list of missing fields
result = agent.process({
    "csv_file_name": "sample-csv.csv"
    # Missing filtered_column_name and value
})
```

## Running Tests

Run the test script to verify the agent works correctly:

```bash
# From the Code directory
python test_csv_filter_agent.py
```

Run the comprehensive examples:

```bash
# From the Code directory
python example_csv_filter_agent.py
```

## API Reference

### CSVFilterAgent Class

#### `__init__(data_dir="data/input")`
Initialize the agent with a data directory.

#### `process(input_data, output_format="json")`
Process a filtering request.
- **input_data**: Dict or JSON string with required fields
- **output_format**: "json", "dict", or "dataframe"
- **Returns**: List of matching records

#### `process_to_json_string(input_data)`
Process and return result as JSON string.

#### `get_headers(csv_file_name)`
Get column names from CSV file.

#### `preview_csv(csv_file_name, n_rows=5)`
Preview CSV with metadata and sample rows.

### Convenience Function

#### `filter_csv(csv_file_name, filtered_column_name, value, data_dir="data/input")`
Quick function to filter CSV and return results.

## Technical Details

- Built on top of the CSVLoader from `src.tools.csv_tools`
- Automatically detects and handles different data types
- Uses pandas for efficient data processing
- Handles boolean string conversions ("TRUE"/"FALSE" → True/False)
- Converts NaN values to None for JSON compatibility
- Includes comprehensive logging for debugging

## License

Part of the Hackathon project.

## Author

AI Assistant
Date: 2024-11-27
