"""
Unit Tests for CSV Tools Module

Tests the CSVLoader class with various scenarios including:
- File loading and validation
- Encoding and delimiter detection
- Data type inference
- Querying and filtering
- Format conversion
- Error handling

Author: AI Assistant
Date: 2024-11-26
"""
import pandas as pd 
import pytest
import tempfile
import os
from pathlib import Path
from typing import List

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import CSVLoader, CSVValidationError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_csv_path():
    """Return path to sample CSV file."""
    return Path(__file__).parent.parent / "data" / "input" / "sample_data.csv"


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,name,value\n")
        f.write("1,Item A,100.50\n")
        f.write("2,Item B,200.75\n")
        f.write("3,Item C,150.25\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def malformed_csv_file():
    """Create a malformed CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,name,value\n")
        f.write("1,Item A,100.50\n")
        f.write("2,Item B\n")  # Missing column
        f.write("3,Item C,150.25,extra\n")  # Extra column
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def csv_with_missing_values():
    """Create a CSV file with missing values."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,name,value,status\n")
        f.write("1,Item A,100.50,active\n")
        f.write("2,,200.75,active\n")  # Missing name
        f.write("3,Item C,,inactive\n")  # Missing value
        f.write("4,Item D,150.25,\n")  # Missing status
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def csv_with_various_delimiters():
    """Create a CSV file with semicolon delimiter."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id;name;value\n")
        f.write("1;Item A;100.50\n")
        f.write("2;Item B;200.75\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


# ============================================================================
# TEST CLASS: File Loading
# ============================================================================

class TestCSVLoaderFileLoading:
    """Test CSV file loading functionality."""
    
    def test_load_valid_csv(self, temp_csv_file):
        """Test loading a valid CSV file."""
        loader = CSVLoader(temp_csv_file)
        df = loader.load()
        
        assert df is not None
        assert len(df) == 3
        assert len(df.columns) == 3
        assert list(df.columns) == ['id', 'name', 'value']
    
    def test_load_nonexistent_file(self):
        """Test error when loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            CSVLoader("/nonexistent/path/file.csv")
    
    def test_load_with_sample_data(self, sample_csv_path):
        """Test loading the sample data file."""
        if sample_csv_path.exists():
            loader = CSVLoader(sample_csv_path)
            df = loader.load()
            
            assert df is not None
            assert len(df) > 0
            assert len(df.columns) > 0
    
    def test_load_without_validation(self, malformed_csv_file):
        """Test loading CSV without validation."""
        loader = CSVLoader(malformed_csv_file)
        # Should not raise error when validation is disabled
        df = loader.load(validate=False)
        assert df is not None
    
    def test_load_with_type_inference(self, temp_csv_file):
        """Test that data types are inferred correctly."""
        loader = CSVLoader(temp_csv_file)
        df = loader.load(infer_types=True)
        
        # 'id' and 'value' should be numeric
        assert pd.api.types.is_numeric_dtype(df['id'])
        assert pd.api.types.is_numeric_dtype(df['value'])
    
    def test_load_without_type_inference(self, temp_csv_file):
        """Test loading without type inference."""
        loader = CSVLoader(temp_csv_file)
        df = loader.load(infer_types=False)
        
        # Everything should be object (string) type
        assert df['id'].dtype == 'object'


# ============================================================================
# TEST CLASS: Validation
# ============================================================================

class TestCSVValidation:
    """Test CSV validation functionality."""
    
    def test_validate_valid_csv(self, temp_csv_file):
        """Test validation of a valid CSV."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        assert loader.validate() is True
    
    def test_validate_empty_dataframe(self):
        """Test validation fails for empty CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,name,value\n")  # Only header, no data
            temp_path = f.name
        
        try:
            loader = CSVLoader(temp_path)
            with pytest.raises(CSVValidationError):
                loader.load(validate=True)
        finally:
            os.unlink(temp_path)
    
    def test_validate_no_columns(self):
        """Test validation fails for file with no columns."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("\n")  # Empty file
            temp_path = f.name
        
        try:
            loader = CSVLoader(temp_path)
            with pytest.raises(CSVValidationError):
                loader.load(validate=True)
        finally:
            os.unlink(temp_path)
    
    def test_validate_duplicate_columns(self):
        """Test validation detects duplicate column names."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id,name,id\n")  # Duplicate 'id'
            f.write("1,Item A,2\n")
            temp_path = f.name
        
        try:
            loader = CSVLoader(temp_path)
            with pytest.raises(CSVValidationError):
                loader.load(validate=True)
        finally:
            os.unlink(temp_path)


# ============================================================================
# TEST CLASS: Metadata
# ============================================================================

class TestCSVMetadata:
    """Test metadata extraction."""
    
    def test_get_metadata(self, temp_csv_file):
        """Test retrieving metadata."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        metadata = loader.get_metadata()
        
        assert 'file_path' in metadata
        assert 'file_size' in metadata
        assert 'row_count' in metadata
        assert 'column_count' in metadata
        assert 'columns' in metadata
        assert 'dtypes' in metadata
        assert 'missing_values' in metadata
        assert 'memory_usage_mb' in metadata
        
        assert metadata['row_count'] == 3
        assert metadata['column_count'] == 3
    
    def test_metadata_columns(self, temp_csv_file):
        """Test metadata column information."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        metadata = loader.get_metadata()
        
        assert set(metadata['columns']) == {'id', 'name', 'value'}
    
    def test_metadata_missing_values(self, csv_with_missing_values):
        """Test metadata tracks missing values."""
        loader = CSVLoader(csv_with_missing_values)
        loader.load()
        
        metadata = loader.get_metadata()
        
        assert metadata['missing_values']['name'] >= 1
        assert metadata['missing_values']['value'] >= 1
        assert metadata['total_missing'] > 0


# ============================================================================
# TEST CLASS: Querying and Filtering
# ============================================================================

class TestCSVQuerying:
    """Test data querying and filtering."""
    
    def test_query_all_data(self, temp_csv_file):
        """Test querying all data (no filters)."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        result = loader.query()
        
        assert len(result) == 3
        assert len(result.columns) == 3
    
    def test_query_with_single_filter(self, temp_csv_file):
        """Test querying with a single filter."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        result = loader.query(filters={'name': 'Item A'})
        
        assert len(result) == 1
        assert result.iloc[0]['name'] == 'Item A'
    
    def test_query_with_multiple_filters(self, temp_csv_file):
        """Test querying with multiple filters."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        result = loader.query(filters={'name': 'Item A', 'id': 1})
        
        assert len(result) == 1
    
    def test_query_with_kwargs_filters(self, temp_csv_file):
        """Test querying with kwargs-style filters."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        result = loader.query(name='Item B')
        
        assert len(result) == 1
        assert result.iloc[0]['name'] == 'Item B'
    
    def test_query_select_columns(self, temp_csv_file):
        """Test querying and selecting specific columns."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        result = loader.query(columns=['id', 'name'])
        
        assert list(result.columns) == ['id', 'name']
        assert 'value' not in result.columns
    
    def test_query_list_filter(self, temp_csv_file):
        """Test querying with list of values (isin)."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        result = loader.query(filters={'name': ['Item A', 'Item B']})
        
        assert len(result) == 2
    
    def test_query_nonexistent_column(self, temp_csv_file):
        """Test querying on non-existent column."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        # Should not raise error, just return full dataset
        result = loader.query(nonexistent_col='value')
        
        assert len(result) == 3  # All rows


# ============================================================================
# TEST CLASS: Format Conversion
# ============================================================================

class TestCSVFormatConversion:
    """Test converting CSV data to different formats."""
    
    def test_to_dataframe(self, temp_csv_file):
        """Test converting to DataFrame."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        df = loader.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
    
    def test_to_dict_records(self, temp_csv_file):
        """Test converting to dict with 'records' orientation."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        data = loader.to_dict(orient='records')
        
        assert isinstance(data, list)
        assert len(data) == 3
        assert all(isinstance(row, dict) for row in data)
        assert 'id' in data[0]
        assert 'name' in data[0]
    
    def test_to_dict_list(self, temp_csv_file):
        """Test converting to dict with 'list' orientation."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        data = loader.to_dict(orient='list')
        
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'name' in data
        assert 'value' in data
        assert isinstance(data['id'], list)
    
    def test_to_dict_handles_nan(self, csv_with_missing_values):
        """Test that to_dict converts NaN to None."""
        loader = CSVLoader(csv_with_missing_values)
        loader.load()
        
        data = loader.to_dict(orient='records')
        
        # Should have None, not NaN
        assert any(row['name'] is None for row in data)


# ============================================================================
# TEST CLASS: Encoding and Delimiter Detection
# ============================================================================

class TestEncodingDelimiterDetection:
    """Test encoding and delimiter detection."""
    
    def test_detect_comma_delimiter(self, temp_csv_file):
        """Test detection of comma delimiter."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        assert loader.delimiter == ','
    
    def test_detect_semicolon_delimiter(self, csv_with_various_delimiters):
        """Test detection of semicolon delimiter."""
        loader = CSVLoader(csv_with_various_delimiters)
        loader.load()
        
        assert loader.delimiter == ';'
    
    def test_detect_utf8_encoding(self, temp_csv_file):
        """Test detection of UTF-8 encoding."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        # Should detect UTF-8 or similar
        assert loader.encoding is not None
    
    def test_explicit_encoding(self):
        """Test explicit encoding specification."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("id,name\n1,Test\n")
            temp_path = f.name
        
        try:
            loader = CSVLoader(temp_path, encoding='utf-8')
            loader.load()
            assert loader.encoding == 'utf-8'
        finally:
            os.unlink(temp_path)
    
    def test_explicit_delimiter(self):
        """Test explicit delimiter specification."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("id;name;value\n1;Item A;100\n")
            temp_path = f.name
        
        try:
            loader = CSVLoader(temp_path, delimiter=';')
            loader.load()
            assert loader.delimiter == ';'
        finally:
            os.unlink(temp_path)


# ============================================================================
# TEST CLASS: Summary and String Representation
# ============================================================================

class TestCSVSummary:
    """Test summary generation and string representation."""
    
    def test_get_summary(self, temp_csv_file):
        """Test getting a summary of the CSV."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        summary = loader.get_summary()
        
        assert isinstance(summary, str)
        assert 'CSV File:' in summary
        assert 'Rows:' in summary
        assert 'Columns:' in summary
        assert '3' in summary  # 3 rows
    
    def test_summary_before_load(self, temp_csv_file):
        """Test summary before loading data."""
        loader = CSVLoader(temp_csv_file)
        
        summary = loader.get_summary()
        
        assert "No data loaded" in summary
    
    def test_string_representation_before_load(self, temp_csv_file):
        """Test string representation before loading."""
        loader = CSVLoader(temp_csv_file)
        
        repr_str = repr(loader)
        
        assert "loaded=False" in repr_str
    
    def test_string_representation_after_load(self, temp_csv_file):
        """Test string representation after loading."""
        loader = CSVLoader(temp_csv_file)
        loader.load()
        
        repr_str = repr(loader)
        
        assert "rows=3" in repr_str
        assert "cols=3" in repr_str


# ============================================================================
# TEST CLASS: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_query_before_load(self, temp_csv_file):
        """Test querying before loading data."""
        loader = CSVLoader(temp_csv_file)
        
        with pytest.raises(ValueError):
            loader.query()
    
    def test_metadata_before_load(self, temp_csv_file):
        """Test getting metadata before loading."""
        loader = CSVLoader(temp_csv_file)
        
        with pytest.raises(ValueError):
            loader.get_metadata()
    
    def test_to_dict_before_load(self, temp_csv_file):
        """Test converting to dict before loading."""
        loader = CSVLoader(temp_csv_file)
        
        with pytest.raises(ValueError):
            loader.to_dict()
    
    def test_to_dataframe_before_load(self, temp_csv_file):
        """Test converting to DataFrame before loading."""
        loader = CSVLoader(temp_csv_file)
        
        with pytest.raises(ValueError):
            loader.to_dataframe()
    
    def test_validate_before_load(self, temp_csv_file):
        """Test validation before loading."""
        loader = CSVLoader(temp_csv_file)
        
        with pytest.raises(CSVValidationError):
            loader.validate()


# ============================================================================
# TEST CLASS: Large Files (Chunking)
# ============================================================================

class TestLargeFileHandling:
    """Test handling of large files with chunking."""
    
    def test_load_with_chunk_size(self, temp_csv_file):
        """Test loading with chunking."""
        loader = CSVLoader(temp_csv_file)
        df = loader.load(chunk_size=2)
        
        assert len(df) == 3
        assert len(df.columns) == 3


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])