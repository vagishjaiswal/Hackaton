"""
CSV Filter Agent

A specialized agent for filtering CSV files based on column values and
returning results in JSON format.

This agent:
1. Accepts JSON input with csv_file_name, filtered_column_name, and value
2. Loads the CSV file
3. Uses the first row as headers (keys)
4. Filters rows where the specified column matches the given value
5. Returns matching rows as a JSON array

Input Format:
{
    "csv_file_name": "sample-csv.csv",
    "filtered_column_name": "Generate",
    "value": true
}

Output Format:
[
    {
        "Focus-Area": "SQL",
        "Color": "Dark Golden & Light yellow",
        "Background": "Black",
        "Generate": true,
        "Count": 0
    }
]

Author: AI Assistant
Date: 2024-11-27
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union
import pandas as pd

from src.tools.csv_tools import CSVLoader


# Configure logging
logger = logging.getLogger(__name__)


class CSVFilterAgent:
    """
    Agent for filtering CSV files based on column values.
    
    This agent provides a simple interface to filter CSV files and return
    results in JSON format. It handles boolean, numeric, and string comparisons.
    
    Attributes:
        data_dir (Path): Directory containing CSV files
        loader (CSVLoader): CSV loader instance
        
    Example:
        ```python
        agent = CSVFilterAgent(data_dir="data/input")
        
        # Process with JSON input
        input_json = {
            "csv_file_name": "sample-csv.csv",
            "filtered_column_name": "Generate",
            "value": True
        }
        
        result = agent.process(input_json)
        print(json.dumps(result, indent=2))
        ```
    """
    
    def __init__(self, data_dir: Union[str, Path] = "data/input"):
        """
        Initialize the CSV Filter Agent.
        
        Args:
            data_dir: Directory containing CSV files (default: "data/input")
        """
        self.data_dir = Path(data_dir)
        self.loader: Optional[CSVLoader] = None
        
        # Validate data directory exists
        if not self.data_dir.exists():
            logger.warning(f"Data directory does not exist: {self.data_dir}")
            logger.info("Will attempt to create it if needed")
        
        logger.info(f"CSV Filter Agent initialized with data_dir: {self.data_dir}")
    
    def _normalize_value(self, value: Any, dtype: str) -> Any:
        """
        Normalize the filter value based on the column's data type.
        
        Args:
            value: The value to normalize
            dtype: The pandas dtype of the column
            
        Returns:
            Normalized value that can be compared with the column
        """
        # Handle boolean strings
        if isinstance(value, str):
            if value.upper() == "TRUE":
                return True
            elif value.upper() == "FALSE":
                return False
        
        # Handle boolean values
        if isinstance(value, bool):
            return value
        
        # Handle numeric types
        if 'int' in dtype.lower():
            try:
                return int(value)
            except (ValueError, TypeError):
                return value
        
        if 'float' in dtype.lower():
            try:
                return float(value)
            except (ValueError, TypeError):
                return value
        
        # Return as-is for strings and other types
        return value
    
    def process(
        self,
        input_data: Union[Dict[str, Any], str],
        output_format: str = "json"
    ) -> Union[List[Dict[str, Any]], str]:
        """
        Process CSV filtering request.
        
        Args:
            input_data: Dictionary or JSON string with:
                - csv_file_name: Name of the CSV file
                - filtered_column_name: Column to filter by
                - value: Value to match in the filtered column
            output_format: Output format ("json", "dict", "dataframe")
            
        Returns:
            List of dictionaries (records) matching the filter criteria
            
        Raises:
            ValueError: If input is invalid
            FileNotFoundError: If CSV file doesn't exist
            KeyError: If filtered column doesn't exist
            
        Example:
            ```python
            # With dict input
            result = agent.process({
                "csv_file_name": "sample-csv.csv",
                "filtered_column_name": "Generate",
                "value": True
            })
            
            # With JSON string input
            result = agent.process('{"csv_file_name": "data.csv", ...}')
            ```
        """
        # Parse input if it's a JSON string
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON input: {e}")
        
        # Validate input structure
        required_fields = ["csv_file_name", "filtered_column_name", "value"]
        missing_fields = [f for f in required_fields if f not in input_data]
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {missing_fields}\n"
                f"Required fields: {required_fields}"
            )
        
        # Extract parameters
        csv_file_name = input_data["csv_file_name"]
        filtered_column_name = input_data["filtered_column_name"]
        filter_value = input_data["value"]
        
        logger.info(f"Processing request: file={csv_file_name}, "
                   f"column={filtered_column_name}, value={filter_value}")
        
        # Construct file path
        csv_file_path = self.data_dir / csv_file_name
        
        # Load CSV file
        try:
            self.loader = CSVLoader(csv_file_path)
            df = self.loader.load(validate=True, infer_types=True)
            logger.info(f"Loaded CSV: {len(df)} rows, {len(df.columns)} columns")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"CSV file not found: {csv_file_path}\n"
                f"Available directory: {self.data_dir}\n"
                f"Please ensure the file exists in the data directory."
            )
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {e}")
        
        # Validate column exists
        if filtered_column_name not in df.columns:
            available_columns = df.columns.tolist()
            raise KeyError(
                f"Column '{filtered_column_name}' not found in CSV.\n"
                f"Available columns: {available_columns}"
            )
        
        # Normalize the filter value based on column type
        dtype = str(df[filtered_column_name].dtype)
        normalized_value = self._normalize_value(filter_value, dtype)
        
        logger.debug(f"Filter value normalized: {filter_value} -> {normalized_value} (type: {type(normalized_value)})")
        
        # Filter the dataframe
        try:
            # Handle boolean filtering
            if isinstance(normalized_value, bool):
                # Try direct boolean comparison
                filtered_df = df[df[filtered_column_name] == normalized_value]
                
                # If no results, try string comparison
                if filtered_df.empty:
                    bool_str = str(normalized_value).upper()
                    filtered_df = df[df[filtered_column_name].astype(str).str.upper() == bool_str]
            else:
                # Standard filtering
                filtered_df = df[df[filtered_column_name] == normalized_value]
            
            logger.info(f"Filtered results: {len(filtered_df)} rows match the criteria")
            
        except Exception as e:
            raise ValueError(f"Failed to filter data: {e}")
        
        # Convert to requested format
        if output_format == "dataframe":
            return filtered_df
        
        # Convert to list of dictionaries (JSON format)
        result = filtered_df.to_dict(orient='records')
        
        # Convert any NaN values to None for JSON compatibility
        result = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in result
        ]
        
        # Return as JSON string or dict
        if output_format == "json":
            return result
        else:
            return result
    
    def process_to_json_string(self, input_data: Union[Dict[str, Any], str]) -> str:
        """
        Process CSV filtering and return result as JSON string.
        
        Args:
            input_data: Input parameters (dict or JSON string)
            
        Returns:
            JSON string with filtered results
            
        Example:
            ```python
            json_result = agent.process_to_json_string({
                "csv_file_name": "sample-csv.csv",
                "filtered_column_name": "Generate",
                "value": True
            })
            print(json_result)
            ```
        """
        result = self.process(input_data, output_format="json")
        return json.dumps(result, indent=2, default=str)
    
    def get_headers(self, csv_file_name: str) -> List[str]:
        """
        Get the headers (column names) from a CSV file.
        
        Args:
            csv_file_name: Name of the CSV file
            
        Returns:
            List of column names
            
        Example:
            ```python
            headers = agent.get_headers("sample-csv.csv")
            print(headers)  # ['Focus-Area', 'Color', 'Background', 'Generate', 'Count']
            ```
        """
        csv_file_path = self.data_dir / csv_file_name
        
        loader = CSVLoader(csv_file_path)
        df = loader.load()
        
        return df.columns.tolist()
    
    def preview_csv(self, csv_file_name: str, n_rows: int = 5) -> Dict[str, Any]:
        """
        Preview a CSV file with metadata and sample rows.
        
        Args:
            csv_file_name: Name of the CSV file
            n_rows: Number of rows to preview (default: 5)
            
        Returns:
            Dictionary with metadata and preview data
            
        Example:
            ```python
            preview = agent.preview_csv("sample-csv.csv")
            print(json.dumps(preview, indent=2))
            ```
        """
        csv_file_path = self.data_dir / csv_file_name
        
        loader = CSVLoader(csv_file_path)
        df = loader.load()
        
        metadata = loader.get_metadata()
        
        preview_data = df.head(n_rows).to_dict(orient='records')
        
        return {
            "file_name": csv_file_name,
            "row_count": metadata["row_count"],
            "column_count": metadata["column_count"],
            "columns": metadata["columns"],
            "dtypes": metadata["dtypes"],
            "preview": preview_data
        }
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"CSVFilterAgent(data_dir='{self.data_dir}')"


# Convenience function for quick filtering
def filter_csv(
    csv_file_name: str,
    filtered_column_name: str,
    value: Any,
    data_dir: Union[str, Path] = "data/input"
) -> List[Dict[str, Any]]:
    """
    Convenience function to quickly filter a CSV file.
    
    Args:
        csv_file_name: Name of the CSV file
        filtered_column_name: Column to filter by
        value: Value to match
        data_dir: Directory containing CSV files
        
    Returns:
        List of dictionaries matching the filter
        
    Example:
        ```python
        from src.agents.csv_filter_agent import filter_csv
        
        result = filter_csv(
            csv_file_name="sample-csv.csv",
            filtered_column_name="Generate",
            value=True
        )
        print(result)
        ```
    """
    agent = CSVFilterAgent(data_dir=data_dir)
    
    input_data = {
        "csv_file_name": csv_file_name,
        "filtered_column_name": filtered_column_name,
        "value": value
    }
    
    return agent.process(input_data)
