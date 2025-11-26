"""
File Saver Agent

An agent that handles saving files with support for:
- Multiple file types (text, JSON, CSV, YAML, binary, etc.)
- Path validation and creation
- Content formatting and validation
- Error handling and backup functionality
- File metadata management

Usage:
    from file_saver_agent import FileSaverAgent
    
    agent = FileSaverAgent()
    
    result = agent.save_file(
        file_path="output/data.json",
        content={"key": "value"},
        file_type="json",
        overwrite=False,
        create_backup=True
    )
    
    print(result)

Author: AI Assistant
Date: 2024-11-27
"""

import json
import os
import csv
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class FileSaveResult:
    """Result of a file save operation"""
    success: bool
    file_path: str
    file_size: int
    message: str
    error: Optional[str] = None
    backup_path: Optional[str] = None
    timestamp: str = None
    content_type: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "message": self.message,
            "error": self.error,
            "backup_path": self.backup_path,
            "timestamp": self.timestamp,
            "content_type": self.content_type,
        }


# ============================================================================
# File Saver Agent
# ============================================================================

class FileSaverAgent:
    """Agent for saving files with various formats and configurations"""
    
    SUPPORTED_FORMATS = {
        "json": "application/json",
        "txt": "text/plain",
        "csv": "text/csv",
        "yaml": "application/x-yaml",
        "yml": "application/x-yaml",
        "xml": "application/xml",
        "html": "text/html",
        "md": "text/markdown",
        "py": "text/x-python",
        "js": "text/javascript",
        "css": "text/css",
        "sql": "text/sql",
        "log": "text/plain",
        "conf": "text/plain",
        "config": "text/plain",
        "ini": "text/plain",
        "properties": "text/plain",
    }
    
    BACKUP_DIR = ".backups"
    
    def __init__(self, backup_enabled: bool = True, max_backups: int = 5):
        """
        Initialize the File Saver Agent
        
        Args:
            backup_enabled: Whether to create backups before overwriting
            max_backups: Maximum number of backups to keep per file
        """
        self.backup_enabled = backup_enabled
        self.max_backups = max_backups
        logger.info(f"FileSaverAgent initialized - Backup enabled: {backup_enabled}")
    
    def save_file(
        self,
        file_path: str,
        content: Any,
        file_type: Optional[str] = None,
        overwrite: bool = True,
        create_backup: bool = True,
        pretty_print: bool = True,
        encoding: str = "utf-8",
    ) -> FileSaveResult:
        """
        Save a file with the given content
        
        Args:
            file_path: Path where file should be saved
            content: Content to save (string, dict, list, etc.)
            file_type: File type (json, csv, txt, etc.). Auto-detected if not provided
            overwrite: Whether to overwrite existing file
            create_backup: Whether to create backup before overwriting
            pretty_print: Whether to pretty-print (for JSON, YAML, etc.)
            encoding: Text encoding (default: utf-8)
            
        Returns:
            FileSaveResult object with operation details
        """
        try:
            # Validate inputs
            if not file_path:
                return FileSaveResult(
                    success=False,
                    file_path="",
                    file_size=0,
                    message="File path is required",
                    error="Invalid file path"
                )
            
            # Normalize path
            file_path = str(Path(file_path))
            
            # Detect file type if not provided
            if not file_type:
                file_type = self._detect_file_type(file_path)
                logger.info(f"Auto-detected file type: {file_type}")
            
            # Validate file type
            if not self._is_supported_format(file_type):
                logger.warning(f"Unsupported file type: {file_type}. Saving as text.")
                file_type = "txt"
            
            # Check if file exists
            path_obj = Path(file_path)
            file_exists = path_obj.exists()
            
            if file_exists and not overwrite:
                return FileSaveResult(
                    success=False,
                    file_path=file_path,
                    file_size=0,
                    message=f"File already exists: {file_path}",
                    error="File exists (overwrite=False)"
                )
            
            # Create backup if needed
            backup_path = None
            if file_exists and create_backup and self.backup_enabled:
                backup_path = self._create_backup(file_path)
                if backup_path:
                    logger.info(f"Created backup: {backup_path}")
            
            # Create parent directories if needed
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Format content based on file type
            formatted_content = self._format_content(content, file_type, pretty_print)
            
            # Save file
            if isinstance(formatted_content, bytes):
                # Binary content
                with open(file_path, 'wb') as f:
                    f.write(formatted_content)
            else:
                # Text content
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(formatted_content)
            
            # Get file size
            file_size = path_obj.stat().st_size
            
            logger.info(f"File saved successfully: {file_path} ({file_size} bytes)")
            
            return FileSaveResult(
                success=True,
                file_path=file_path,
                file_size=file_size,
                message=f"File saved successfully: {file_path}",
                backup_path=backup_path,
                content_type=self.SUPPORTED_FORMATS.get(file_type, "application/octet-stream")
            )
        
        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(error_msg)
            return FileSaveResult(
                success=False,
                file_path=file_path,
                file_size=0,
                message="Permission denied",
                error=error_msg
            )
        
        except OSError as e:
            error_msg = f"OS error: {e}"
            logger.error(error_msg)
            return FileSaveResult(
                success=False,
                file_path=file_path,
                file_size=0,
                message="OS error occurred",
                error=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return FileSaveResult(
                success=False,
                file_path=file_path,
                file_size=0,
                message="Failed to save file",
                error=error_msg
            )
    
    def save_json(
        self,
        file_path: str,
        content: Dict[str, Any],
        pretty_print: bool = True,
        **kwargs
    ) -> FileSaveResult:
        """
        Save JSON file
        
        Args:
            file_path: Path for JSON file
            content: Dictionary or list to save
            pretty_print: Whether to pretty-print JSON
            **kwargs: Additional arguments for save_file
            
        Returns:
            FileSaveResult object
        """
        return self.save_file(
            file_path=file_path,
            content=content,
            file_type="json",
            pretty_print=pretty_print,
            **kwargs
        )
    
    def save_csv(
        self,
        file_path: str,
        content: List[Dict[str, Any]],
        **kwargs
    ) -> FileSaveResult:
        """
        Save CSV file
        
        Args:
            file_path: Path for CSV file
            content: List of dictionaries to save as CSV
            **kwargs: Additional arguments for save_file
            
        Returns:
            FileSaveResult object
        """
        return self.save_file(
            file_path=file_path,
            content=content,
            file_type="csv",
            **kwargs
        )
    
    def save_text(
        self,
        file_path: str,
        content: str,
        **kwargs
    ) -> FileSaveResult:
        """
        Save text file
        
        Args:
            file_path: Path for text file
            content: String content to save
            **kwargs: Additional arguments for save_file
            
        Returns:
            FileSaveResult object
        """
        return self.save_file(
            file_path=file_path,
            content=content,
            file_type="txt",
            **kwargs
        )
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type from extension"""
        try:
            ext = Path(file_path).suffix.lstrip('.').lower()
            if ext in self.SUPPORTED_FORMATS:
                return ext
            return "txt"  # Default to text
        except Exception:
            return "txt"
    
    def _is_supported_format(self, file_type: str) -> bool:
        """Check if file type is supported"""
        return file_type.lower() in self.SUPPORTED_FORMATS or file_type == "txt"
    
    def _format_content(
        self,
        content: Any,
        file_type: str,
        pretty_print: bool = True
    ) -> Union[str, bytes]:
        """Format content based on file type"""
        file_type = file_type.lower()
        
        # JSON format
        if file_type == "json":
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass
            
            if pretty_print:
                return json.dumps(content, indent=2, default=str)
            else:
                return json.dumps(content, default=str)
        
        # CSV format
        elif file_type == "csv":
            if not isinstance(content, list):
                raise ValueError("CSV content must be a list of dictionaries")
            
            if not content:
                return ""
            
            if not isinstance(content[0], dict):
                raise ValueError("CSV content must be a list of dictionaries")
            
            # Get fieldnames from first row
            fieldnames = list(content[0].keys())
            
            # Create CSV content using StringIO
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write rows
            writer.writerows(content)
            
            return output.getvalue()
        
        # YAML format
        elif file_type in ["yaml", "yml"]:
            try:
                import yaml
                if pretty_print:
                    return yaml.dump(content, default_flow_style=False)
                else:
                    return yaml.dump(content)
            except ImportError:
                logger.warning("PyYAML not installed. Saving as JSON instead.")
                return json.dumps(content, indent=2, default=str)
        
        # XML format
        elif file_type == "xml":
            try:
                import xml.etree.ElementTree as ET
                if isinstance(content, str):
                    return content
                # Simple dict to XML conversion
                root = ET.Element("root")
                self._dict_to_xml(content, root)
                return ET.tostring(root, encoding="unicode")
            except Exception as e:
                logger.warning(f"XML formatting failed: {e}. Saving as text.")
                return str(content)
        
        # Default: convert to string
        else:
            if isinstance(content, (dict, list)):
                return json.dumps(content, indent=2, default=str)
            return str(content)
    
    def _dict_to_xml(self, data: Dict, parent):
        """Convert dictionary to XML elements"""
        try:
            import xml.etree.ElementTree as ET
            for key, value in data.items():
                if isinstance(value, dict):
                    child = ET.SubElement(parent, key)
                    self._dict_to_xml(value, child)
                elif isinstance(value, list):
                    for item in value:
                        child = ET.SubElement(parent, key)
                        if isinstance(item, dict):
                            self._dict_to_xml(item, child)
                        else:
                            child.text = str(item)
                else:
                    child = ET.SubElement(parent, key)
                    child.text = str(value)
        except Exception as e:
            logger.warning(f"Error converting dict to XML: {e}")
    
    def _create_backup(self, file_path: str) -> Optional[str]:
        """Create a backup of existing file"""
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                return None
            
            # Create backup directory
            backup_dir = Path(self.BACKUP_DIR)
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{path_obj.stem}_{timestamp}{path_obj.suffix}"
            backup_path = backup_dir / backup_name
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            
            # Clean old backups
            self._cleanup_old_backups(path_obj.stem, path_obj.suffix)
            
            return str(backup_path)
        
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
            return None
    
    def _cleanup_old_backups(self, file_stem: str, file_ext: str) -> None:
        """Remove old backup files, keeping only max_backups"""
        try:
            backup_dir = Path(self.BACKUP_DIR)
            
            if not backup_dir.exists():
                return
            
            # Find all backups for this file
            pattern = f"{file_stem}_*{file_ext}"
            backups = sorted(backup_dir.glob(pattern), key=os.path.getctime, reverse=True)
            
            # Remove old backups
            for backup in backups[self.max_backups:]:
                backup.unlink()
                logger.info(f"Removed old backup: {backup}")
        
        except Exception as e:
            logger.warning(f"Error cleaning up old backups: {e}")
    
    def list_backups(self, file_path: str) -> List[str]:
        """List all backups for a file"""
        try:
            path_obj = Path(file_path)
            backup_dir = Path(self.BACKUP_DIR)
            
            if not backup_dir.exists():
                return []
            
            pattern = f"{path_obj.stem}_*{path_obj.suffix}"
            backups = sorted(
                backup_dir.glob(pattern),
                key=os.path.getctime,
                reverse=True
            )
            
            return [str(b) for b in backups]
        
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def restore_backup(self, file_path: str, backup_index: int = 0) -> FileSaveResult:
        """Restore file from backup"""
        try:
            backups = self.list_backups(file_path)
            
            if not backups:
                return FileSaveResult(
                    success=False,
                    file_path=file_path,
                    file_size=0,
                    message="No backups found",
                    error="No backups available"
                )
            
            if backup_index >= len(backups):
                return FileSaveResult(
                    success=False,
                    file_path=file_path,
                    file_size=0,
                    message=f"Backup index out of range (max: {len(backups)-1})",
                    error="Invalid backup index"
                )
            
            backup_path = backups[backup_index]
            shutil.copy2(backup_path, file_path)
            
            file_size = Path(file_path).stat().st_size
            
            logger.info(f"Restored file from backup: {backup_path}")
            
            return FileSaveResult(
                success=True,
                file_path=file_path,
                file_size=file_size,
                message=f"File restored from backup",
                backup_path=backup_path
            )
        
        except Exception as e:
            error_msg = f"Error restoring backup: {str(e)}"
            logger.error(error_msg)
            return FileSaveResult(
                success=False,
                file_path=file_path,
                file_size=0,
                message="Failed to restore backup",
                error=error_msg
            )


# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Example usage of FileSaverAgent"""
    print("\n" + "="*80)
    print("FILE SAVER AGENT - EXAMPLES")
    print("="*80)
    
    agent = FileSaverAgent(backup_enabled=True, max_backups=3)
    
    # Example 1: Save JSON file
    print("\n[EXAMPLE 1] Saving JSON file...")
    data = {
        "name": "John Doe",
        "role": "Data Scientist",
        "skills": ["Python", "Machine Learning", "Data Analysis"],
        "experience_years": 5
    }
    
    result = agent.save_json(
        file_path="output/user_profile.json",
        content=data,
        overwrite=True
    )
    print(json.dumps(result.to_dict(), indent=2))
    
    # Example 2: Save CSV file
    print("\n[EXAMPLE 2] Saving CSV file...")
    csv_data = [
        {"user_id": 1, "name": "John Doe", "role": "Data Scientist"},
        {"user_id": 2, "name": "Jane Smith", "role": "Engineer"},
        {"user_id": 3, "name": "Bob Johnson", "role": "Manager"}
    ]
    
    result = agent.save_csv(
        file_path="output/users.csv",
        content=csv_data,
        overwrite=True
    )
    print(json.dumps(result.to_dict(), indent=2))
    
    # Example 3: Save text file
    print("\n[EXAMPLE 3] Saving text file...")
    text_content = "This is a sample text file.\nIt contains multiple lines.\nLine 3."
    
    result = agent.save_text(
        file_path="output/sample.txt",
        content=text_content,
        overwrite=True
    )
    print(json.dumps(result.to_dict(), indent=2))
    
    # Example 4: Save with auto-detected format
    print("\n[EXAMPLE 4] Saving with auto-detected format...")
    result = agent.save_file(
        file_path="output/config.yaml",
        content={"database": {"host": "localhost", "port": 5432}},
        overwrite=True
    )
    print(json.dumps(result.to_dict(), indent=2))
    
    # Example 5: List backups
    print("\n[EXAMPLE 5] Listing backups...")
    backups = agent.list_backups("output/user_profile.json")
    print(f"Found {len(backups)} backups:")
    for i, backup in enumerate(backups):
        print(f"  [{i}] {backup}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
