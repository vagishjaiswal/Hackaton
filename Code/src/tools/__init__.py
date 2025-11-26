"""
Tools Module - Utilities for AI Agents

This module provides tools that AI agents can use to interact with data and external systems.

Available Tools:
- CSVLoader: Load, validate, and query CSV files

Usage:
    from src.tools import CSVLoader
    
    loader = CSVLoader("data/input/sample_data.csv")
    loader.load()
    
    # Get metadata
    metadata = loader.get_metadata()
    
    # Query data
    filtered = loader.query(category="Electronics")
    
    # Convert to dict
    data = loader.to_dict()

Author: AI Assistant
Date: 2024-11-26
"""

from .csv_tools import CSVLoader, CSVValidationError

__all__ = [
    "CSVLoader",
    "CSVValidationError",
]

__version__ = "0.1.0"
