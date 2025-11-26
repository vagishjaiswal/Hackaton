# CSV Filter Agent - Quick Start

## 🚀 Quick Start (30 seconds)

### Step 1: Run the Test
```bash
cd Code
python test_csv_filter_agent.py
```

Expected output: All tests pass ✅

### Step 2: Try the Examples
```bash
python example_csv_filter_agent.py
```

### Step 3: Use in Your Code
```python
from src.agents.csv_filter_agent import filter_csv

# Filter for rows where Generate=True
result = filter_csv(
    csv_file_name="sample-csv.csv",
    filtered_column_name="Generate",
    value=True,
    data_dir="data/input"
)

print(result)
# Output: [{"Focus-Area": "SQL", "Color": "Dark Golden & Light yellow", ...}]
```

## 📝 Input Format

```json
{
  "csv_file_name": "sample-csv.csv",
  "filtered_column_name": "Generate",
  "value": true
}
```

## 📤 Output Format

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

## 🎯 Common Use Cases

### 1. Basic Filtering
```python
from src.agents.csv_filter_agent import CSVFilterAgent

agent = CSVFilterAgent(data_dir="data/input")

# Filter by boolean
result = agent.process({
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": True
})
```

### 2. Filter by String
```python
result = agent.process({
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Focus-Area",
    "value": "Azure"
})
```

### 3. Filter by Number
```python
result = agent.process({
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Count",
    "value": 0
})
```

### 4. Get JSON String
```python
json_str = agent.process_to_json_string({
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": True
})
print(json_str)
```

### 5. Command Line Usage
```bash
# Using JSON file
python csv_filter_standalone.py --input data/input/filter_input_example.json --pretty

# Using arguments
python csv_filter_standalone.py --csv sample-csv.csv --column Generate --value true --pretty

# Save output
python csv_filter_standalone.py --csv sample-csv.csv --column Generate --value true --output results.json
```

## 🛠️ Utility Functions

### Get CSV Headers
```python
headers = agent.get_headers("sample-csv.csv")
print(headers)
# ['Focus-Area', 'Color', 'Background', 'Generate', 'Count']
```

### Preview CSV
```python
preview = agent.preview_csv("sample-csv.csv", n_rows=3)
print(preview)
# Shows metadata and first 3 rows
```

## ⚠️ Error Handling

```python
try:
    result = agent.process({
        "csv_file_name": "missing.csv",
        "filtered_column_name": "Generate",
        "value": True
    })
except FileNotFoundError as e:
    print(f"File not found: {e}")
except KeyError as e:
    print(f"Column not found: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```

## 📚 Full Documentation

See `docs/csv_filter_agent_guide.md` for complete documentation.

## 🎓 Examples

See `example_csv_filter_agent.py` for 10 comprehensive examples.

## ✅ That's It!

You're ready to use the CSV Filter Agent. Happy coding! 🎉
