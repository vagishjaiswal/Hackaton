"""
Tools Module - Utilities for AI Agents

This module provides tools that AI agents can use to interact with data and external systems.

Available Tools:
- CSVLoader: Load, validate, and query CSV files
- TinyDBAuditManager: Audit logging and workflow tracking
- AuditLogTool: Log agent actions to audit system
- WorkflowStatusTool: Track workflow status
- AuditQueryTool: Query audit data
- ExportAuditTool: Export and manage audit data

Usage:
    from src.tools import CSVLoader, AuditLogTool, TinyDBAuditManager
    
    # CSV Loading
    loader = CSVLoader("data/input/sample_data.csv")
    loader.load()
    metadata = loader.get_metadata()
    
    # Audit System
    audit_mgr = TinyDBAuditManager()
    exec_id = audit_mgr.start_workflow("wf_123")
    audit_mgr.log_agent_action("wf_123", exec_id, "Agent", "action")
    audit_mgr.end_workflow("wf_123", exec_id, "completed")

Author: AI Assistant
Date: 2024-11-27
"""

from .csv_tools import CSVLoader, CSVValidationError
from .audit_manager import TinyDBAuditManager
from .audit_tools import (
    AuditLogTool,
    WorkflowStatusTool,
    AuditQueryTool,
    ExportAuditTool
)

__all__ = [
    # CSV Tools
    "CSVLoader",
    "CSVValidationError",
    # Audit System
    "TinyDBAuditManager",
    "AuditLogTool",
    "WorkflowStatusTool",
    "AuditQueryTool",
    "ExportAuditTool",
]

__version__ = "0.2.0"
