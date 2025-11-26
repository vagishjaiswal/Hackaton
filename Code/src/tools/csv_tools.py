"""
CSV Tools Module

This module provides utilities for loading, validating, and querying CSV files.
Designed for use by AI agents to analyze structured data.

Features:
- Pandas-based CSV handling
- Automatic encoding detection
- Schema validation
- Data type inference
- Query and filter capabilities
- Support for large files with chunking
- Comprehensive error handling

Author: AI Assistant
Date: 2024-11-26
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import chardet


# Configure logging
logger = logging.getLogger(__name__)


class CSVValidationError(Exception):
    """Raised when CSV validation fails."""
    pass


class CSVLoader:
    """
    A robust CSV file loader with validation and query capabilities.
    
    This class provides a high-level interface for loading and working with
    CSV files. It handles common issues like encoding detection, missing values,
    and various CSV formats.
    
    Attributes:
        file_path (Path): Path to the CSV file
        df (pd.DataFrame): Loaded DataFrame (None until load() is called)
        encoding (str): Detected or specified encoding
        delimiter (str): CSV delimiter used
        
    Example:
        ```python
        loader = CSVLoader("data/input/sample_data.csv")
        loader.load()
        
        # Get metadata
        metadata = loader.get_metadata()
        print(f"Rows: {metadata['row_count']}")
        
        # Query data
        filtered = loader.query(category="Electronics")
        
        # Convert to dict
        data_dict = loader.to_dict()
        ```
    """
    
    def __init__(
        self,
        file_path: Union[str, Path],
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None
    ):
        """
        Initialize the CSV loader.
        
        Args:
            file_path: Path to the CSV file
            encoding: Character encoding (auto-detected if None)
            delimiter: CSV delimiter (auto-detected if None)
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.encoding = encoding
        self.delimiter = delimiter
        
        # Validate file exists
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {self.file_path}\n"
                f"Please ensure the file exists at the specified path."
            )
        
        logger.info(f"Initialized CSVLoader for: {self.file_path}")
    
    def _detect_encoding(self) -> str:
        """
        Detect the character encoding of the file.
        
        Returns:
            Detected encoding as string
        """
        if self.encoding:
            return self.encoding
        
        try:
            with open(self.file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.info(
                    f"Detected encoding: {encoding} "
                    f"(confidence: {confidence:.2%})"
                )
                
                return encoding or 'utf-8'
                
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}. Using UTF-8")
            return 'utf-8'
    
    def _detect_delimiter(self) -> str:
        """
        Detect the CSV delimiter by reading the first line.
        
        Returns:
            Detected delimiter character
        """
        if self.delimiter:
            return self.delimiter
        
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                first_line = f.readline()
                
            # Count common delimiters
            delimiters = [',', ';', '\t', '|']
            counts = {d: first_line.count(d) for d in delimiters}
            
            # Choose delimiter with highest count
            delimiter = max(counts, key=counts.get)
            
            if counts[delimiter] == 0:
                logger.warning("No delimiter detected, defaulting to comma")
                return ','
            
            logger.info(f"Detected delimiter: '{delimiter}'")
            return delimiter
            
        except Exception as e:
            logger.warning(f"Delimiter detection failed: {e}. Using comma")
            return ','
    
    def load(
        self,
        validate: bool = True,
        infer_types: bool = True,
        chunk_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load the CSV file into a pandas DataFrame.
        
        Args:
            validate: Whether to validate the CSV structure
            infer_types: Whether to infer and convert data types
            chunk_size: If set, load file in chunks (for large files)
            
        Returns:
            Loaded DataFrame
            
        Raises:
            CSVValidationError: If validation fails
            pd.errors.ParserError: If CSV parsing fails
            
        Example:
            ```python
            loader = CSVLoader("data.csv")
            df = loader.load()
            print(df.head())
            ```
        """
        try:
            # Detect encoding and delimiter
            self.encoding = self._detect_encoding()
            self.delimiter = self._detect_delimiter()
            
            logger.info(f"Loading CSV with encoding={self.encoding}, delimiter='{self.delimiter}'")
            
            # Load CSV
            if chunk_size:
                # Load in chunks for large files
                chunks = []
                for chunk in pd.read_csv(
                    self.file_path,
                    encoding=self.encoding,
                    delimiter=self.delimiter,
                    chunksize=chunk_size,
                    low_memory=False
                ):
                    chunks.append(chunk)
                self.df = pd.concat(chunks, ignore_index=True)
                logger.info(f"Loaded {len(chunks)} chunks")
            else:
                # Load entire file
                self.df = pd.read_csv(
                    self.file_path,
                    encoding=self.encoding,
                    delimiter=self.delimiter,
                    low_memory=False
                )
            
            logger.info(f"Successfully loaded CSV: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            
            # Infer and convert data types
            if infer_types:
                self._infer_types()
            
            # Validate if requested
            if validate:
                self.validate()
            
            return self.df
            
        except pd.errors.ParserError as e:
            error_msg = (
                f"Failed to parse CSV file: {self.file_path}\n"
                f"Error: {e}\n"
                f"This usually means the file is malformed or has inconsistent columns."
            )
            logger.error(error_msg)
            raise CSVValidationError(error_msg)
            
        except UnicodeDecodeError as e:
            error_msg = (
                f"Encoding error reading file: {self.file_path}\n"
                f"Tried encoding: {self.encoding}\n"
                f"Try specifying a different encoding (e.g., 'latin-1', 'cp1252')"
            )
            logger.error(error_msg)
            raise CSVValidationError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error loading CSV: {e}"
            logger.error(error_msg)
            raise
    
    def _infer_types(self) -> None:
        """
        Infer and convert column data types automatically.
        
        Attempts to convert:
        - Numeric strings to int/float
        - Date strings to datetime
        - Boolean strings to bool
        """
        if self.df is None:
            return
        
        for col in self.df.columns:
            # Skip if already numeric or datetime
            if pd.api.types.is_numeric_dtype(self.df[col]) or \
               pd.api.types.is_datetime64_any_dtype(self.df[col]):
                continue
            
            # Try to convert to numeric
            try:
                converted = pd.to_numeric(self.df[col], errors='coerce')
                # Only convert if most values are not NaN
                if converted.notna().sum() / len(converted) > 0.5:
                    self.df[col] = converted
                    logger.debug(f"Converted column '{col}' to numeric")
                    continue
            except:
                pass
            
            # Try to convert to datetime
            try:
                converted = pd.to_datetime(self.df[col], errors='coerce')
                if converted.notna().sum() / len(converted) > 0.5:
                    self.df[col] = converted
                    logger.debug(f"Converted column '{col}' to datetime")
                    continue
            except:
                pass
            
            # Try to convert to boolean
            if self.df[col].dtype == 'object':
                unique_vals = self.df[col].dropna().unique()
                if len(unique_vals) <= 2:
                    bool_map = {
                        'true': True, 'false': False,
                        'yes': True, 'no': False,
                        '1': True, '0': False,
                        't': True, 'f': False
                    }
                    lower_vals = {str(v).lower() for v in unique_vals}
                    if lower_vals.issubset(bool_map.keys()):
                        self.df[col] = self.df[col].str.lower().map(bool_map)
                        logger.debug(f"Converted column '{col}' to boolean")
    
    def validate(self) -> bool:
        """
        Validate the loaded CSV data.
        
        Checks:
        - DataFrame is not empty
        - Has at least one column
        - Column names are unique
        - No completely empty columns
        
        Returns:
            True if validation passes
            
        Raises:
            CSVValidationError: If validation fails
        """
        if self.df is None:
            raise CSVValidationError("No data loaded. Call load() first.")
        
        # Check if empty
        if self.df.empty:
            raise CSVValidationError(
                f"CSV file is empty: {self.file_path}"
            )
        
        # Check for columns
        if len(self.df.columns) == 0:
            raise CSVValidationError(
                f"CSV file has no columns: {self.file_path}"
            )
        
        # Check for duplicate column names
        duplicates = self.df.columns[self.df.columns.duplicated()].tolist()
        if duplicates:
            raise CSVValidationError(
                f"Duplicate column names found: {duplicates}"
            )
        
        # Check for completely empty columns
        empty_cols = self.df.columns[self.df.isna().all()].tolist()
        if empty_cols:
            logger.warning(f"Completely empty columns found: {empty_cols}")
        
        logger.info("CSV validation passed")
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the loaded CSV file.
        
        Returns:
            Dictionary containing:
            - file_path: Path to the file
            - file_size: File size in bytes
            - row_count: Number of rows
            - column_count: Number of columns
            - columns: List of column names
            - dtypes: Data types for each column
            - missing_values: Count of missing values per column
            - memory_usage: Memory usage in MB
            
        Example:
            ```python
            metadata = loader.get_metadata()
            print(f"Rows: {metadata['row_count']}")
            print(f"Columns: {metadata['columns']}")
            ```
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")
        
        # Calculate file size
        file_size = self.file_path.stat().st_size
        
        # Get missing value counts
        missing_values = self.df.isna().sum().to_dict()
        
        # Get memory usage
        memory_usage = self.df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
        
        metadata = {
            'file_path': str(self.file_path),
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'row_count': len(self.df),
            'column_count': len(self.df.columns),
            'columns': self.df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'missing_values': missing_values,
            'total_missing': sum(missing_values.values()),
            'memory_usage_mb': round(memory_usage, 2),
            'encoding': self.encoding,
            'delimiter': self.delimiter
        }
        
        return metadata
    
    def query(
        self,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Query the CSV data with filters.
        
        Args:
            filters: Dictionary of column:value pairs to filter by
            columns: List of columns to return (None = all columns)
            **kwargs: Alternative way to specify filters (column=value)
            
        Returns:
            Filtered DataFrame
            
        Example:
            ```python
            # Filter by category
            electronics = loader.query(category="Electronics")
            
            # Filter and select columns
            names = loader.query(
                filters={"status": "active"},
                columns=["id", "name"]
            )
            
            # Multiple filters
            result = loader.query(category="Electronics", status="active")
            ```
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")
        
        # Combine filters from both sources
        all_filters = filters or {}
        all_filters.update(kwargs)
        
        # Start with full DataFrame
        result = self.df.copy()
        
        # Apply filters
        for col, value in all_filters.items():
            if col not in result.columns:
                logger.warning(f"Column '{col}' not found in DataFrame")
                continue
            
            if isinstance(value, (list, tuple)):
                # Multiple values - use isin
                result = result[result[col].isin(value)]
            else:
                # Single value - direct comparison
                result = result[result[col] == value]
        
        # Select columns if specified
        if columns:
            # Validate columns exist
            valid_cols = [c for c in columns if c in result.columns]
            if len(valid_cols) != len(columns):
                invalid = set(columns) - set(valid_cols)
                logger.warning(f"Columns not found: {invalid}")
            result = result[valid_cols]
        
        logger.debug(f"Query returned {len(result)} rows")
        return result
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Get the loaded data as a pandas DataFrame.
        
        Returns:
            DataFrame containing the CSV data
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")
        
        return self.df.copy()
    
    def to_dict(
        self,
        orient: str = 'records',
        include_index: bool = False
    ) -> Union[List[Dict], Dict]:
        """
        Convert the CSV data to a dictionary.
        
        Args:
            orient: Format of the dictionary:
                - 'records': list of dicts (one per row)
                - 'dict': dict of dicts {column: {index: value}}
                - 'list': dict of lists {column: [values]}
                - 'series': dict of Series {column: Series}
                - 'split': dict with 'index', 'columns', 'data'
                - 'index': dict with row index as keys
            include_index: Whether to include the DataFrame index
            
        Returns:
            Dictionary representation of the data
            
        Example:
            ```python
            # List of records (most common)
            records = loader.to_dict()  # [{col1: val1, col2: val2}, ...]
            
            # Dict of lists
            lists = loader.to_dict(orient='list')  # {col1: [vals], col2: [vals]}
            ```
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load() first.")
        
        # Convert NaN to None for JSON compatibility
        df = self.df.copy()
        df = df.where(pd.notna(df), None)
        
        # Convert datetime to string for JSON compatibility
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
        
        return df.to_dict(orient=orient)
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the CSV data.
        
        Returns:
            Multi-line string with summary information
            
        Example:
            ```python
            print(loader.get_summary())
            ```
        """
        if self.df is None:
            return "No data loaded. Call load() first."
        
        metadata = self.get_metadata()
        
        summary_lines = [
            f"CSV File: {metadata['file_path']}",
            f"File Size: {metadata['file_size_mb']} MB",
            f"Encoding: {metadata['encoding']}",
            f"Delimiter: '{metadata['delimiter']}'",
            "",
            f"Rows: {metadata['row_count']:,}",
            f"Columns: {metadata['column_count']}",
            "",
            "Column Information:",
        ]
        
        # Add column details
        for col in metadata['columns']:
            dtype = metadata['dtypes'][col]
            missing = metadata['missing_values'][col]
            missing_pct = (missing / metadata['row_count'] * 100) if metadata['row_count'] > 0 else 0
            
            summary_lines.append(
                f"  - {col}: {dtype} "
                f"(missing: {missing}/{metadata['row_count']} = {missing_pct:.1f}%)"
            )
        
        summary_lines.extend([
            "",
            f"Total Missing Values: {metadata['total_missing']:,}",
            f"Memory Usage: {metadata['memory_usage_mb']:.2f} MB"
        ])
        
        return "\n".join(summary_lines)
    
    def __repr__(self) -> str:
        """String representation of the CSVLoader."""
        if self.df is None:
            return f"CSVLoader(file='{self.file_path}', loaded=False)"
        return (
            f"CSVLoader(file='{self.file_path}', "
            f"rows={len(self.df)}, cols={len(self.df.columns)})"
        )
