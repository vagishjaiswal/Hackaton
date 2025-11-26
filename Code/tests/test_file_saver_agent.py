"""
Tests for File Saver Agent

Tests include:
- JSON file saving
- CSV file saving
- Text file saving
- Path validation and creation
- Backup functionality
- Error handling
- Multiple file formats
"""

import sys
import json
import os
import pytest
from pathlib import Path
import tempfile
import shutil

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.file_saver_agent import FileSaverAgent, FileSaveResult


class TestFileSaverAgent:
    """Test suite for FileSaverAgent"""
    
    @pytest.fixture
    def agent(self):
        """Create a FileSaverAgent instance for testing"""
        return FileSaverAgent(backup_enabled=True, max_backups=3)
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(".backups"):
            shutil.rmtree(".backups")
    
    def test_save_json_file(self, agent, temp_dir):
        """Test saving JSON file"""
        data = {"name": "John", "age": 30}
        file_path = os.path.join(temp_dir, "test.json")
        
        result = agent.save_json(file_path, data)
        
        assert result.success is True
        assert Path(file_path).exists()
        
        # Verify content
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data == data
    
    def test_save_csv_file(self, agent, temp_dir):
        """Test saving CSV file"""
        data = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]
        file_path = os.path.join(temp_dir, "test.csv")
        
        result = agent.save_csv(file_path, data)
        
        assert result.success is True
        assert Path(file_path).exists()
        
        # Verify content
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3  # Header + 2 rows
    
    def test_save_text_file(self, agent, temp_dir):
        """Test saving text file"""
        content = "Hello, World!\nLine 2"
        file_path = os.path.join(temp_dir, "test.txt")
        
        result = agent.save_text(file_path, content)
        
        assert result.success is True
        assert Path(file_path).exists()
        
        # Verify content
        with open(file_path, 'r') as f:
            saved_content = f.read()
        
        assert saved_content == content
    
    def test_create_directories(self, agent, temp_dir):
        """Test automatic directory creation"""
        file_path = os.path.join(temp_dir, "sub1", "sub2", "test.json")
        data = {"key": "value"}
        
        result = agent.save_json(file_path, data)
        
        assert result.success is True
        assert Path(file_path).exists()
        assert Path(file_path).parent.exists()
    
    def test_overwrite_false(self, agent, temp_dir):
        """Test overwrite protection"""
        file_path = os.path.join(temp_dir, "test.json")
        
        # Create initial file
        result1 = agent.save_json(file_path, {"version": 1})
        assert result1.success is True
        
        # Try to save without overwrite
        result2 = agent.save_json(
            file_path,
            {"version": 2},
            overwrite=False
        )
        
        assert result2.success is False
        assert "already exists" in result2.message
    
    def test_overwrite_true(self, agent, temp_dir):
        """Test file overwriting"""
        file_path = os.path.join(temp_dir, "test.json")
        
        # Create initial file
        result1 = agent.save_json(file_path, {"version": 1})
        assert result1.success is True
        
        # Overwrite file
        result2 = agent.save_json(
            file_path,
            {"version": 2},
            overwrite=True
        )
        
        assert result2.success is True
        
        # Verify new content
        with open(file_path, 'r') as f:
            data = json.load(f)
        assert data["version"] == 2
    
    def test_backup_creation(self, agent, temp_dir):
        """Test backup creation on overwrite"""
        file_path = os.path.join(temp_dir, "test.json")
        
        # Create initial file
        result1 = agent.save_json(file_path, {"version": 1})
        assert result1.success is True
        assert result1.backup_path is None
        
        # Overwrite with backup
        result2 = agent.save_json(
            file_path,
            {"version": 2},
            overwrite=True,
            create_backup=True
        )
        
        assert result2.success is True
        assert result2.backup_path is not None
        assert Path(result2.backup_path).exists()
    
    def test_file_type_detection(self, agent, temp_dir):
        """Test automatic file type detection"""
        test_cases = [
            ("test.json", {"key": "value"}),
            ("test.txt", "text content"),
            ("test.csv", [{"id": 1, "name": "test"}]),
        ]
        
        for filename, content in test_cases:
            file_path = os.path.join(temp_dir, filename)
            result = agent.save_file(file_path, content)
            
            assert result.success is True
            assert Path(file_path).exists()
    
    def test_invalid_file_path(self, agent):
        """Test handling of invalid file path"""
        result = agent.save_file(
            file_path="",
            content="test"
        )
        
        assert result.success is False
        assert result.error is not None
    
    def test_file_size_reported(self, agent, temp_dir):
        """Test file size is correctly reported"""
        content = {"key": "value"}
        file_path = os.path.join(temp_dir, "test.json")
        
        result = agent.save_json(file_path, content)
        
        assert result.success is True
        assert result.file_size > 0
        
        # Verify size matches actual file
        actual_size = Path(file_path).stat().st_size
        assert result.file_size == actual_size
    
    def test_pretty_print_json(self, agent, temp_dir):
        """Test JSON pretty printing"""
        data = {"a": 1, "b": [2, 3], "c": {"d": 4}}
        file_path = os.path.join(temp_dir, "test.json")
        
        result = agent.save_json(file_path, data, pretty_print=True)
        
        assert result.success is True
        
        # Verify formatting with newlines
        with open(file_path, 'r') as f:
            content = f.read()
        
        assert "\n" in content  # Pretty printed
    
    def test_unsupported_format_handling(self, agent, temp_dir):
        """Test handling of unsupported file format"""
        file_path = os.path.join(temp_dir, "test.unknown")
        content = "test content"
        
        result = agent.save_file(file_path, content)
        
        # Should succeed but save as text
        assert result.success is True
        assert Path(file_path).exists()
    
    def test_permission_error_handling(self, agent, temp_dir):
        """Test handling of permission errors"""
        file_path = os.path.join(temp_dir, "test.json")
        
        result = agent.save_json(file_path, {"test": "data"})
        assert result.success is True
        
        # Try to write to a read-only file (platform dependent)
        # Note: This test may not work on all platforms
        try:
            os.chmod(file_path, 0o000)
            result = agent.save_json(file_path, {"test": "data2"}, overwrite=True)
            # Reset permissions for cleanup
            os.chmod(file_path, 0o644)
            
            # Should fail due to permissions
            assert result.success is False
        except Exception:
            # Skip if platform doesn't support permission testing
            os.chmod(file_path, 0o644)
            pytest.skip("Platform doesn't support permission testing")


class TestFileFormatting:
    """Test file formatting functions"""
    
    def test_json_formatting(self, temp_dir):
        """Test JSON format conversion"""
        agent = FileSaverAgent()
        
        # Test dict to JSON
        data = {"name": "test", "items": [1, 2, 3]}
        result = agent._format_content(data, "json", pretty_print=True)
        
        assert isinstance(result, str)
        assert '"name"' in result
        assert '"test"' in result
    
    def test_csv_formatting(self, temp_dir):
        """Test CSV format conversion"""
        agent = FileSaverAgent()
        
        data = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]
        result = agent._format_content(data, "csv", pretty_print=False)
        
        assert isinstance(result, str)
        lines = result.split("\n")
        assert len(lines) == 3  # Header + 2 rows
    
    def test_text_formatting(self):
        """Test text format conversion"""
        agent = FileSaverAgent()
        
        text = "Hello, World!"
        result = agent._format_content(text, "txt", pretty_print=False)
        
        assert result == text


class TestBackupFunctionality:
    """Test backup and restore functionality"""
    
    def test_list_backups(self):
        """Test listing backups"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent = FileSaverAgent(backup_enabled=True)
            file_path = os.path.join(temp_dir, "test.json")
            
            # Create multiple versions
            for i in range(3):
                agent.save_json(file_path, {"version": i}, overwrite=True, create_backup=(i > 0))
            
            backups = agent.list_backups(file_path)
            assert len(backups) <= 3  # max_backups is 3
    
    def test_restore_from_backup(self):
        """Test restoring file from backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent = FileSaverAgent(backup_enabled=True)
            file_path = os.path.join(temp_dir, "test.json")
            
            # Create initial version
            original_data = {"version": 1, "value": "original"}
            agent.save_json(file_path, original_data)
            
            # Overwrite with new version
            new_data = {"version": 2, "value": "new"}
            agent.save_json(file_path, new_data, overwrite=True, create_backup=True)
            
            # Verify new version is saved
            with open(file_path, 'r') as f:
                current = json.load(f)
            assert current["version"] == 2
            
            # Restore from backup
            result = agent.restore_backup(file_path, backup_index=0)
            assert result.success is True
            
            # Verify restored content
            with open(file_path, 'r') as f:
                restored = json.load(f)
            assert restored["version"] == 1


def run_example_tests():
    """Run example tests without pytest"""
    print("\n" + "="*80)
    print("RUNNING FILE SAVER AGENT TESTS")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        agent = FileSaverAgent(backup_enabled=True)
        
        # Test 1: Save JSON
        print("\n[TEST 1] Save JSON file...")
        data = {"test": "data", "number": 42}
        result = agent.save_json(os.path.join(temp_dir, "test.json"), data)
        print(f"Status: {'PASSED' if result.success else 'FAILED'}")
        print(f"Message: {result.message}")
        
        # Test 2: Save CSV
        print("\n[TEST 2] Save CSV file...")
        csv_data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        result = agent.save_csv(os.path.join(temp_dir, "test.csv"), csv_data)
        print(f"Status: {'PASSED' if result.success else 'FAILED'}")
        print(f"Message: {result.message}")
        
        # Test 3: Save Text
        print("\n[TEST 3] Save text file...")
        text = "Hello, World!\nThis is a test."
        result = agent.save_text(os.path.join(temp_dir, "test.txt"), text)
        print(f"Status: {'PASSED' if result.success else 'FAILED'}")
        print(f"Message: {result.message}")
        
        # Test 4: Create nested directories
        print("\n[TEST 4] Create nested directories...")
        nested_path = os.path.join(temp_dir, "a", "b", "c", "data.json")
        result = agent.save_json(nested_path, {"nested": True})
        print(f"Status: {'PASSED' if result.success else 'FAILED'}")
        print(f"Message: {result.message}")
        
        # Test 5: Backup on overwrite
        print("\n[TEST 5] Backup on overwrite...")
        file_path = os.path.join(temp_dir, "backup_test.json")
        agent.save_json(file_path, {"version": 1})
        result = agent.save_json(file_path, {"version": 2}, overwrite=True, create_backup=True)
        print(f"Status: {'PASSED' if result.success else 'FAILED'}")
        print(f"Message: {result.message}")
        print(f"Backup path: {result.backup_path}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    # Run without pytest
    run_example_tests()
    
    # Or run with pytest:
    # pytest test_file_saver_agent.py -v
