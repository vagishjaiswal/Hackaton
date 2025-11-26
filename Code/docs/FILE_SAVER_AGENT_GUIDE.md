# File Saver Agent - Comprehensive Guide

## Overview

The **File Saver Agent** is a robust Python utility designed to handle file saving operations with support for multiple file formats, automatic path creation, backup functionality, and comprehensive error handling.

## Features

✅ **Multiple File Formats**
- JSON, CSV, TXT, YAML, XML, HTML, MD, Python, JavaScript, SQL, and more
- Auto-detection of file type from extension
- Smart content formatting for each format

✅ **Path Management**
- Automatic creation of nested directories
- Path validation and normalization
- Cross-platform compatibility (Windows/Linux/macOS)

✅ **Backup & Recovery**
- Automatic backup creation before overwriting
- Backup management with configurable retention
- Restore from backup functionality
- Timestamped backup naming

✅ **Error Handling**
- Comprehensive exception handling
- Permission error detection
- File existence validation
- Detailed error messages and logging

✅ **Content Processing**
- Pretty-printing for JSON/YAML
- Automatic encoding handling
- Dict-to-CSV conversion
- Dict-to-XML conversion

## Installation

```python
# Add to your project
from src.agents.file_saver_agent import FileSaverAgent
```

## Quick Start

### Basic Usage

```python
from src.agents.file_saver_agent import FileSaverAgent

# Initialize agent
agent = FileSaverAgent()

# Save JSON file
data = {"name": "John Doe", "role": "Engineer"}
result = agent.save_json(
    file_path="output/user.json",
    content=data
)

print(result.message)  # File saved successfully
```

### Supported Methods

#### 1. **save_json()** - Save JSON files

```python
data = {
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "count": 2
}

result = agent.save_json(
    file_path="data/users.json",
    content=data,
    pretty_print=True,
    overwrite=True
)
```

**Parameters:**
- `file_path` (str): Path where file will be saved
- `content` (dict/list): Data to save
- `pretty_print` (bool): Format JSON with indentation (default: True)
- `overwrite` (bool): Overwrite existing file (default: True)
- `create_backup` (bool): Create backup before overwriting (default: True)

---

#### 2. **save_csv()** - Save CSV files

```python
records = [
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 2, "name": "Bob", "score": 87},
    {"id": 3, "name": "Charlie", "score": 92}
]

result = agent.save_csv(
    file_path="output/results.csv",
    content=records,
    overwrite=True
)
```

**Parameters:**
- `file_path` (str): Path for CSV file
- `content` (list[dict]): List of dictionaries to save
- `overwrite` (bool): Overwrite existing file
- `create_backup` (bool): Create backup before overwriting

**Note:** Content must be a list of dictionaries. Keys become column headers.

---

#### 3. **save_text()** - Save text files

```python
content = """
Project Summary
===============

This project implements a file saving agent.
It supports multiple file formats and provides
robust error handling.
"""

result = agent.save_text(
    file_path="docs/summary.txt",
    content=content
)
```

**Parameters:**
- `file_path` (str): Path for text file
- `content` (str): Text content to save
- `overwrite` (bool): Overwrite existing file
- `create_backup` (bool): Create backup before overwriting

---

#### 4. **save_file()** - Generic file saver

```python
# Auto-detect format from extension
result = agent.save_file(
    file_path="config/app.yaml",
    content={"database": {"host": "localhost"}},
    file_type="yaml"  # Optional: auto-detected if not provided
)

# Or with explicit format
result = agent.save_file(
    file_path="output/data.xml",
    content={"root": {"item": "value"}},
    file_type="xml"
)
```

**Parameters:**
- `file_path` (str): Path where file will be saved
- `content` (Any): Content to save (auto-formatted)
- `file_type` (str): Format type (auto-detected if not provided)
- `overwrite` (bool): Overwrite existing file (default: True)
- `create_backup` (bool): Create backup before overwriting (default: True)
- `pretty_print` (bool): Pretty-print formatted content (default: True)
- `encoding` (str): Text encoding (default: utf-8)

## Advanced Features

### Backup Management

#### Create Backups

```python
# Backup is created automatically when overwriting
result = agent.save_json(
    file_path="data/settings.json",
    content={"theme": "dark"},
    overwrite=True,
    create_backup=True  # Creates backup before overwriting
)

print(result.backup_path)  # Path to created backup
```

#### List Backups

```python
# View all backups for a file
backups = agent.list_backups("data/settings.json")

for i, backup_path in enumerate(backups):
    print(f"[{i}] {backup_path}")
```

**Output:**
```
[0] .backups/settings_20241127_143022.json
[1] .backups/settings_20241127_140015.json
[2] .backups/settings_20241127_135005.json
```

#### Restore from Backup

```python
# Restore most recent backup (index 0)
result = agent.restore_backup("data/settings.json", backup_index=0)

if result.success:
    print(f"Restored from: {result.backup_path}")
```

### File Type Detection

```python
# Automatic detection based on extension
test_cases = [
    ("data.json", {"key": "value"}),      # Detected as JSON
    ("notes.txt", "Some text"),            # Detected as TEXT
    ("table.csv", [{"id": 1}]),           # Detected as CSV
    ("config.yaml", {"db": "mysql"}),     # Detected as YAML
]

for file_path, content in test_cases:
    result = agent.save_file(file_path, content)
    # File type auto-detected and handled appropriately
```

### Error Handling

```python
result = agent.save_json("data.json", {"test": "data"})

if result.success:
    print(f"✓ File saved: {result.file_path}")
    print(f"  Size: {result.file_size} bytes")
    print(f"  Type: {result.content_type}")
else:
    print(f"✗ Error: {result.error}")
    print(f"  Message: {result.message}")
```

**Common Errors:**
- `File already exists (overwrite=False)` - File exists and overwrite is disabled
- `Permission denied` - Insufficient write permissions
- `Invalid file path` - Empty or invalid path provided
- `OS error` - System-level file operation error

### File Size Management

```python
# File size is automatically reported
result = agent.save_json("output/data.json", large_dict)

print(f"File size: {result.file_size} bytes")
print(f"File size: {result.file_size / 1024:.2f} KB")
```

## Real-World Examples

### Example 1: Data Export Pipeline

```python
from src.agents.file_saver_agent import FileSaverAgent
import json

agent = FileSaverAgent(backup_enabled=True)

# Export user data
users_data = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]

# Save as JSON
agent.save_json(
    file_path="exports/users.json",
    content=users_data,
    pretty_print=True
)

# Save as CSV
agent.save_csv(
    file_path="exports/users.csv",
    content=users_data
)

print("✓ Data exported successfully")
```

### Example 2: Configuration Management

```python
# Load configuration
config = {
    "app": {
        "name": "MyApp",
        "version": "1.0.0",
        "debug": False
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp_db"
    }
}

# Save configuration
result = agent.save_json(
    file_path="config/app_config.json",
    content=config,
    overwrite=True,
    create_backup=True  # Keep previous configs
)

if result.success:
    print(f"✓ Config saved: {result.file_path}")
```

### Example 3: Log File Aggregation

```python
# Aggregate logs
logs = [
    {"timestamp": "2024-11-27 10:00:00", "level": "INFO", "message": "App started"},
    {"timestamp": "2024-11-27 10:05:00", "level": "ERROR", "message": "Connection failed"},
    {"timestamp": "2024-11-27 10:10:00", "level": "INFO", "message": "Reconnected"},
]

# Save as JSON
agent.save_json(
    file_path="logs/aggregated.json",
    content={"logs": logs, "count": len(logs)}
)

# Save as CSV
agent.save_csv(
    file_path="logs/aggregated.csv",
    content=logs
)
```

### Example 4: Report Generation

```python
# Generate report
report = """
MONTHLY REPORT - NOVEMBER 2024
==============================

Executive Summary:
- Total Users: 1,250
- Active Users: 945
- Growth Rate: 12.5%

Metrics:
- Engagement: 78%
- Retention: 85%
- Churn Rate: 3%

Recommendations:
1. Improve user onboarding
2. Enhance mobile experience
3. Add premium features
"""

result = agent.save_text(
    file_path="reports/november_2024.txt",
    content=report
)

print(f"Report saved: {result.file_path}")
```

### Example 5: Batch File Processing

```python
# Process multiple files
files_to_save = {
    "users.json": user_data,
    "products.json": product_data,
    "orders.json": order_data,
    "analytics.json": analytics_data,
}

for filename, data in files_to_save.items():
    result = agent.save_json(
        file_path=f"output/{filename}",
        content=data,
        overwrite=True,
        create_backup=True
    )
    
    status = "✓" if result.success else "✗"
    print(f"{status} {filename} ({result.file_size} bytes)")
```

## Configuration Options

### Initialize with Custom Settings

```python
# Custom backup configuration
agent = FileSaverAgent(
    backup_enabled=True,      # Enable backup functionality
    max_backups=5             # Keep last 5 backups per file
)
```

**Options:**
- `backup_enabled` (bool): Enable/disable backup creation
- `max_backups` (int): Maximum number of backups to retain per file

## Supported File Formats

| Format | Extension | MIME Type | Auto-Format |
|--------|-----------|-----------|------------|
| JSON | .json | application/json | ✓ |
| CSV | .csv | text/csv | ✓ |
| Plain Text | .txt | text/plain | ✓ |
| YAML | .yaml, .yml | application/x-yaml | ✓ |
| XML | .xml | application/xml | ✓ |
| HTML | .html | text/html | ✓ |
| Markdown | .md | text/markdown | ✓ |
| Python | .py | text/x-python | ✗ |
| JavaScript | .js | text/javascript | ✗ |
| CSS | .css | text/css | ✗ |
| SQL | .sql | text/sql | ✗ |
| Config | .conf, .config | text/plain | ✗ |
| INI | .ini | text/plain | ✗ |
| Properties | .properties | text/plain | ✗ |
| Logs | .log | text/plain | ✗ |

## Result Object

### FileSaveResult

Every save operation returns a `FileSaveResult` object:

```python
result = agent.save_json("data.json", {"test": "data"})

# Access result properties
print(result.success)          # bool: Operation success status
print(result.file_path)        # str: Full path to saved file
print(result.file_size)        # int: Size in bytes
print(result.message)          # str: Human-readable message
print(result.error)            # str: Error description (if failed)
print(result.backup_path)      # str: Path to backup (if created)
print(result.timestamp)        # str: ISO timestamp of operation
print(result.content_type)     # str: MIME type of file

# Convert to dictionary
result_dict = result.to_dict()
print(json.dumps(result_dict, indent=2))
```

**Output Example:**
```json
{
  "success": true,
  "file_path": "/path/to/data.json",
  "file_size": 247,
  "message": "File saved successfully: /path/to/data.json",
  "error": null,
  "backup_path": ".backups/data_20241127_143022.json",
  "timestamp": "2024-11-27T14:30:22.123456",
  "content_type": "application/json"
}
```

## Logging

The agent includes comprehensive logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

agent = FileSaverAgent()
# Now all operations will be logged with DEBUG level
```

**Log Output Examples:**
```
2024-11-27 14:30:22,123 - file_saver_agent - INFO - FileSaverAgent initialized - Backup enabled: True
2024-11-27 14:30:22,456 - file_saver_agent - INFO - Auto-detected file type: json
2024-11-27 14:30:22,789 - file_saver_agent - INFO - Created backup: .backups/data_20241127_143022.json
2024-11-27 14:30:22,999 - file_saver_agent - INFO - File saved successfully: /path/to/data.json (247 bytes)
```

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest Code/tests/test_file_saver_agent.py -v

# Run specific test
pytest Code/tests/test_file_saver_agent.py::TestFileSaverAgent::test_save_json_file -v

# Run with coverage
pytest Code/tests/test_file_saver_agent.py --cov=src.agents.file_saver_agent
```

### Run Example Tests

```bash
python Code/src/agents/file_saver_agent.py
```

## Performance Considerations

- **File Size**: Handles files of any size (tested up to 1GB+)
- **Directory Creation**: Efficiently creates nested directories
- **Backup Cleanup**: Automatically manages old backups to save storage
- **Encoding**: Optimized UTF-8 handling with fallback support

## Best Practices

1. **Always check result status**
   ```python
   result = agent.save_json("data.json", data)
   if not result.success:
       print(f"Error: {result.error}")
   ```

2. **Use meaningful file paths**
   ```python
   # Good
   agent.save_json("output/reports/2024/november.json", data)
   
   # Avoid
   agent.save_json("data.json", data)
   ```

3. **Enable backups for important files**
   ```python
   agent.save_json(
       "config/settings.json",
       settings,
       create_backup=True
   )
   ```

4. **Handle encoding properly**
   ```python
   agent.save_file(
       "data/unicode.txt",
       unicode_content,
       encoding="utf-8"
   )
   ```

5. **Use pretty printing for human-readable files**
   ```python
   agent.save_json(
       "config/app.json",
       config,
       pretty_print=True
   )
   ```

## Troubleshooting

### Issue: Permission Denied

```python
# Solution: Check file permissions or use different path
result = agent.save_json("output/data.json", data)
if "Permission denied" in str(result.error):
    # Try alternative path or check OS permissions
    result = agent.save_json("/tmp/data.json", data)
```

### Issue: File Already Exists

```python
# Solution 1: Enable overwrite
result = agent.save_json("data.json", data, overwrite=True)

# Solution 2: Use different filename
result = agent.save_json(f"data_{timestamp}.json", data)
```

### Issue: Large File Size

```python
# Solution: Stream or compress data before saving
import json
data_str = json.dumps(data, default=str)
result = agent.save_text("data.json", data_str)
```

## API Reference

See `src/agents/file_saver_agent.py` for complete API documentation.

## License

This utility is part of the AI Hackathon project.

## Support

For issues or questions, refer to the test files in `Code/tests/test_file_saver_agent.py` for usage examples.
