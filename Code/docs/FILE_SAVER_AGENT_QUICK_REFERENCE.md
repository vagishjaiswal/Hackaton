# File Saver Agent - Quick Reference

## Quick Start

```python
from src.agents.file_saver_agent import FileSaverAgent

agent = FileSaverAgent()

# Save JSON
agent.save_json("data.json", {"key": "value"})

# Save CSV
agent.save_csv("data.csv", [{"id": 1, "name": "Alice"}])

# Save text
agent.save_text("notes.txt", "Hello World")
```

## API Methods

### Core Methods

| Method | Parameters | Returns | Example |
|--------|-----------|---------|---------|
| `save_file()` | `file_path, content, file_type, overwrite, create_backup, pretty_print, encoding` | `FileSaveResult` | `agent.save_file("data.json", data)` |
| `save_json()` | `file_path, content, pretty_print, **kwargs` | `FileSaveResult` | `agent.save_json("users.json", users)` |
| `save_csv()` | `file_path, content, **kwargs` | `FileSaveResult` | `agent.save_csv("users.csv", users)` |
| `save_text()` | `file_path, content, **kwargs` | `FileSaveResult` | `agent.save_text("notes.txt", text)` |

### Backup Methods

| Method | Parameters | Returns | Example |
|--------|-----------|---------|---------|
| `list_backups()` | `file_path` | `List[str]` | `agent.list_backups("data.json")` |
| `restore_backup()` | `file_path, backup_index` | `FileSaveResult` | `agent.restore_backup("data.json", 0)` |

## Common Patterns

### Pattern 1: Save with Backup

```python
result = agent.save_json(
    file_path="config.json",
    content=config_data,
    overwrite=True,
    create_backup=True  # Creates timestamped backup
)
```

### Pattern 2: Batch Save

```python
files = {
    "users.json": users_data,
    "products.json": products_data,
}

for filename, data in files.items():
    result = agent.save_json(f"output/{filename}", data)
    print(f"{'✓' if result.success else '✗'} {filename}")
```

### Pattern 3: Error Handling

```python
result = agent.save_json("data.json", data)

if not result.success:
    print(f"Error: {result.error}")
else:
    print(f"Saved: {result.file_path} ({result.file_size} bytes)")
```

### Pattern 4: Configuration Management

```python
agent = FileSaverAgent(backup_enabled=True, max_backups=5)

# Save with backup
result = agent.save_json("config/app.json", config, create_backup=True)

# List previous versions
backups = agent.list_backups("config/app.json")

# Restore if needed
if len(backups) > 0:
    agent.restore_backup("config/app.json", backup_index=0)
```

## File Format Support

| Format | Extension | Auto-Format | Notes |
|--------|-----------|-------------|-------|
| JSON | `.json` | ✓ | Pretty-printed with indentation |
| CSV | `.csv` | ✓ | Requires list of dicts |
| Text | `.txt` | ✓ | Plain text, no formatting |
| YAML | `.yaml`, `.yml` | ✓ | Requires PyYAML package |
| XML | `.xml` | ✓ | Simple dict-to-XML conversion |
| HTML | `.html` | ✗ | Saved as plain text |
| Markdown | `.md` | ✗ | Saved as plain text |
| Python | `.py` | ✗ | Saved as plain text |
| JavaScript | `.js` | ✗ | Saved as plain text |

## Result Object

```python
result = agent.save_json("data.json", data)

# Properties
result.success          # True if save succeeded
result.file_path        # Full path to saved file
result.file_size        # Size in bytes
result.message          # Human-readable message
result.error            # Error message (if failed)
result.backup_path      # Path to backup (if created)
result.timestamp        # ISO timestamp of operation
result.content_type     # MIME type

# Methods
result.to_dict()        # Convert to dictionary
```

## Configuration Options

```python
# Initialize with custom settings
agent = FileSaverAgent(
    backup_enabled=True,    # Enable backup functionality
    max_backups=5          # Keep last 5 backups per file
)
```

## Common Scenarios

### Scenario 1: Export Multiple Formats

```python
data = [{"id": 1, "name": "Alice"}]

agent.save_json("output/data.json", data)
agent.save_csv("output/data.csv", data)
agent.save_text("output/data.txt", str(data))
```

### Scenario 2: Protect Important Files

```python
# Try to overwrite without permission
result = agent.save_json(
    "important.json",
    new_data,
    overwrite=False  # Prevent accidental overwrites
)

if not result.success:
    print("File is protected - create backup first")
```

### Scenario 3: Auto-create Directories

```python
# Creates nested directories automatically
result = agent.save_json(
    "deep/nested/path/to/data.json",
    data
)
```

### Scenario 4: Handle Errors Gracefully

```python
result = agent.save_json("data.json", data)

if result.success:
    print(f"✓ Saved {result.file_size} bytes")
else:
    if "already exists" in result.message:
        # Handle file exists
        pass
    elif "Permission" in result.message:
        # Handle permission error
        pass
    else:
        # Handle other errors
        pass
```

## Logging

Enable debug logging to see detailed operation logs:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now all file operations are logged
```

Log messages show:
- File operations (save, create backup, restore)
- File type detection
- File sizes
- Success/failure messages

## Performance Tips

1. **Use pretty_print=False for large files**
   ```python
   agent.save_json("large.json", big_data, pretty_print=False)
   ```

2. **Disable backups for temporary files**
   ```python
   agent.save_json("temp.json", data, create_backup=False)
   ```

3. **Batch process files**
   ```python
   for data in large_list:
       agent.save_json(f"file_{i}.json", data)
   ```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `FileNotFoundError` | Parent directory doesn't exist - use auto-created path |
| `PermissionError` | Check file/directory permissions |
| `File already exists` | Use `overwrite=True` or `overwrite=False` as needed |
| `UnicodeDecodeError` | Specify correct `encoding` parameter |
| `Unsupported format` | Use `file_type` parameter to override |

## Files Location

- **Main Agent**: `Code/src/agents/file_saver_agent.py`
- **Tests**: `Code/tests/test_file_saver_agent.py`
- **Examples**: `Code/tests/workflow/example_file_saver_agent.py`
- **Documentation**: `Code/docs/FILE_SAVER_AGENT_GUIDE.md`
- **Generated Files**: `Code/examples/` (after running examples)

## Quick Examples

### Save User Data
```python
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]

agent.save_json("users.json", users)
agent.save_csv("users.csv", users)
```

### Save Configuration
```python
config = {
    "app": {"name": "MyApp", "version": "1.0"},
    "db": {"host": "localhost", "port": 5432}
}

agent.save_json("config.json", config)
```

### Generate Report
```python
report = f"""
MONTHLY REPORT
==============
Users: {user_count}
Revenue: ${revenue}
Orders: {order_count}
"""

agent.save_text("report.txt", report)
```

## Dependencies

- Python 3.7+
- PyYAML (optional, for YAML support)

## See Also

- `FILE_SAVER_AGENT_GUIDE.md` - Complete guide with examples
- `example_file_saver_agent.py` - Practical usage examples
- `test_file_saver_agent.py` - Unit tests and test patterns
