"""
File Saver Agent - Practical Examples

Demonstrates real-world usage scenarios for the File Saver Agent
"""

import sys
import json
from pathlib import Path

# Add parent path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.file_saver_agent import FileSaverAgent


def example_1_data_export():
    """Example 1: Export application data in multiple formats"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Data Export Pipeline")
    print("="*80)
    
    agent = FileSaverAgent(backup_enabled=True)
    
    # Application data
    users_data = [
        {"id": 1, "name": "Alice Johnson", "role": "Engineer", "email": "alice@company.com"},
        {"id": 2, "name": "Bob Smith", "role": "Manager", "email": "bob@company.com"},
        {"id": 3, "name": "Charlie Brown", "role": "Designer", "email": "charlie@company.com"},
    ]
    
    # Export as JSON
    result_json = agent.save_json(
        file_path="examples/exports/users.json",
        content=users_data,
        pretty_print=True,
        overwrite=True
    )
    print(f"\n[JSON Export] {result_json.message}")
    print(f"  File size: {result_json.file_size} bytes")
    
    # Export as CSV
    result_csv = agent.save_csv(
        file_path="examples/exports/users.csv",
        content=users_data,
        overwrite=True
    )
    print(f"\n[CSV Export] {result_csv.message}")
    print(f"  File size: {result_csv.file_size} bytes")
    
    # Export as text with custom formatting
    text_content = "USER DIRECTORY\n" + "="*50 + "\n"
    for user in users_data:
        text_content += f"\n{user['name']}\n"
        text_content += f"  Role: {user['role']}\n"
        text_content += f"  Email: {user['email']}\n"
    
    result_text = agent.save_text(
        file_path="examples/exports/users.txt",
        content=text_content,
        overwrite=True
    )
    print(f"\n[Text Export] {result_text.message}")
    print(f"  File size: {result_text.file_size} bytes")


def example_2_configuration_management():
    """Example 2: Configuration file management with backups"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Configuration Management with Backups")
    print("="*80)
    
    agent = FileSaverAgent(backup_enabled=True, max_backups=5)
    
    # Application configuration
    config = {
        "app": {
            "name": "DataProcessor",
            "version": "2.0.1",
            "debug": False,
            "log_level": "INFO"
        },
        "database": {
            "host": "db.company.com",
            "port": 5432,
            "name": "app_prod",
            "connection_timeout": 30
        },
        "features": {
            "enable_caching": True,
            "max_workers": 4,
            "batch_size": 1000
        }
    }
    
    config_path = "examples/config/app_config.json"
    
    # Save initial configuration
    result = agent.save_json(
        file_path=config_path,
        content=config,
        pretty_print=True,
        overwrite=True,
        create_backup=False  # First save, no backup needed
    )
    print(f"\n[Initial Config] {result.message}")
    
    # Update configuration
    config["app"]["version"] = "2.0.2"
    config["features"]["batch_size"] = 2000
    
    result = agent.save_json(
        file_path=config_path,
        content=config,
        pretty_print=True,
        overwrite=True,
        create_backup=True  # Create backup before overwriting
    )
    print(f"\n[Updated Config] {result.message}")
    if result.backup_path:
        print(f"  Backup created: {result.backup_path}")
    
    # List available backups
    backups = agent.list_backups(config_path)
    print(f"\n[Backups] Found {len(backups)} backup(s)")
    for i, backup in enumerate(backups):
        print(f"  [{i}] {backup}")


def example_3_report_generation():
    """Example 3: Generate and save reports in multiple formats"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Report Generation")
    print("="*80)
    
    agent = FileSaverAgent(backup_enabled=True)
    
    # Sales data
    sales_data = [
        {"month": "January", "revenue": 45000, "orders": 320, "avg_order": 140.63},
        {"month": "February", "revenue": 52000, "orders": 345, "avg_order": 150.72},
        {"month": "March", "revenue": 58500, "orders": 390, "avg_order": 150.00},
        {"month": "April", "revenue": 61000, "orders": 410, "avg_order": 148.78},
    ]
    
    # Save as JSON (for system processing)
    result_json = agent.save_json(
        file_path="examples/reports/quarterly_sales.json",
        content={
            "period": "Q1 2024",
            "sales": sales_data,
            "total_revenue": sum(s["revenue"] for s in sales_data),
            "total_orders": sum(s["orders"] for s in sales_data)
        },
        pretty_print=True,
        overwrite=True
    )
    print(f"\n[JSON Report] {result_json.message}")
    
    # Save as CSV (for Excel import)
    result_csv = agent.save_csv(
        file_path="examples/reports/quarterly_sales.csv",
        content=sales_data,
        overwrite=True
    )
    print(f"[CSV Report] {result_csv.message}")
    
    # Create text report (human-readable)
    report = "QUARTERLY SALES REPORT - Q1 2024\n"
    report += "=" * 60 + "\n\n"
    report += "MONTHLY BREAKDOWN\n"
    report += "-" * 60 + "\n"
    report += f"{'Month':<12} {'Revenue':>12} {'Orders':>10} {'Avg Order':>12}\n"
    report += "-" * 60 + "\n"
    
    for row in sales_data:
        report += f"{row['month']:<12} ${row['revenue']:>10,} {row['orders']:>10} ${row['avg_order']:>11.2f}\n"
    
    report += "-" * 60 + "\n"
    total_rev = sum(s["revenue"] for s in sales_data)
    total_ord = sum(s["orders"] for s in sales_data)
    report += f"{'TOTAL':<12} ${total_rev:>10,} {total_ord:>10}\n"
    report += "-" * 60 + "\n\n"
    
    result_text = agent.save_text(
        file_path="examples/reports/quarterly_sales.txt",
        content=report,
        overwrite=True
    )
    print(f"[Text Report] {result_text.message}")


def example_4_batch_processing():
    """Example 4: Process and save multiple files in batch"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Batch File Processing")
    print("="*80)
    
    agent = FileSaverAgent(backup_enabled=True)
    
    # Multiple datasets
    datasets = {
        "users": {
            "description": "User profiles",
            "data": [
                {"id": 1, "name": "Alice", "department": "Engineering"},
                {"id": 2, "name": "Bob", "department": "Sales"},
            ]
        },
        "products": {
            "description": "Product catalog",
            "data": [
                {"id": "P001", "name": "Widget", "price": 29.99},
                {"id": "P002", "name": "Gadget", "price": 49.99},
            ]
        },
        "inventory": {
            "description": "Stock levels",
            "data": [
                {"product_id": "P001", "quantity": 100},
                {"product_id": "P002", "quantity": 45},
            ]
        }
    }
    
    print("\nProcessing batch files...\n")
    results = {}
    
    for name, dataset in datasets.items():
        result = agent.save_json(
            file_path=f"examples/batch/{name}.json",
            content=dataset["data"],
            pretty_print=True,
            overwrite=True
        )
        
        status = "[OK]" if result.success else "[FAILED]"
        print(f"{status} {name:<15} - {result.message}")
        results[name] = result
    
    # Summary
    successful = sum(1 for r in results.values() if r.success)
    print(f"\n[SUMMARY] {successful}/{len(results)} files saved successfully")
    total_size = sum(r.file_size for r in results.values())
    print(f"[SUMMARY] Total size: {total_size} bytes")


def example_5_error_handling():
    """Example 5: Error handling and recovery"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Error Handling and Recovery")
    print("="*80)
    
    agent = FileSaverAgent(backup_enabled=True)
    
    print("\n[Test 1] Empty file path...")
    result = agent.save_json("", {"test": "data"})
    print(f"Result: {result.message}")
    print(f"Error: {result.error}")
    
    print("\n[Test 2] Invalid file type (auto-convert)...")
    result = agent.save_file(
        file_path="examples/test/unknown.xyz",
        content={"data": "test"},
        file_type="xyz"  # Unsupported format
    )
    print(f"Result: {result.message}")
    print(f"Content type: {result.content_type}")
    
    print("\n[Test 3] Overwrite protection...")
    file_path = "examples/test/protected.json"
    
    # Create initial file
    result1 = agent.save_json(file_path, {"version": 1})
    print(f"Created: {result1.message}")
    
    # Try to overwrite without permission
    result2 = agent.save_json(
        file_path,
        {"version": 2},
        overwrite=False
    )
    print(f"Overwrite attempt: {result2.message}")
    print(f"Error: {result2.error}")
    
    print("\n[Test 4] File size reporting...")
    large_data = {
        f"key_{i}": f"value_{i}" * 10
        for i in range(100)
    }
    result = agent.save_json(
        file_path="examples/test/large.json",
        content=large_data,
        pretty_print=True,
        overwrite=True
    )
    print(f"File size: {result.file_size} bytes ({result.file_size / 1024:.2f} KB)")


def example_6_different_formats():
    """Example 6: Working with different file formats"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Multiple File Formats")
    print("="*80)
    
    agent = FileSaverAgent(backup_enabled=True)
    
    # Sample data
    data = {
        "application": "DataProcessor",
        "version": "1.0.0",
        "settings": {
            "threads": 4,
            "timeout": 30,
            "retry_count": 3
        }
    }
    
    # Save as different formats
    formats = {
        "json": ("examples/formats/config.json", {}),
        "yaml": ("examples/formats/config.yaml", {}),
    }
    
    for fmt, (filepath, kwargs) in formats.items():
        result = agent.save_file(
            file_path=filepath,
            content=data,
            file_type=fmt,
            pretty_print=True,
            overwrite=True
        )
        print(f"\n[{fmt.upper():6}] {result.message}")
        print(f"        Size: {result.file_size} bytes")
        print(f"        Type: {result.content_type}")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("FILE SAVER AGENT - PRACTICAL EXAMPLES")
    print("="*80)
    
    try:
        example_1_data_export()
        example_2_configuration_management()
        example_3_report_generation()
        example_4_batch_processing()
        example_5_error_handling()
        example_6_different_formats()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nCheck the 'examples/' directory for generated files.")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
