"""
TinyDB Audit Tool for Agents

This module provides tools for agents to interact with the TinyDB audit system.
Agents can use these tools to:
- Log their actions
- Query audit history
- Get metrics
- Report errors

Author: AI Assistant
Date: 2024-11-27
"""

from typing import Any, Dict, List, Optional
from src.agents import BaseTool
from src.tools.audit_manager import TinyDBAuditManager


# ============================================================================
# Audit Tools
# ============================================================================

class AuditLogTool(BaseTool):
    """
    Tool for logging agent actions to audit system.
    
    Example:
        ```python
        tool = AuditLogTool(audit_manager)
        result = tool.execute(
            workflow_id="wf_123",
            execution_id="exec_1",
            agent_name="DataAnalyst",
            action="analyze_csv",
            status="success",
            duration_ms=150.5
        )
        ```
    """
    
    def __init__(self, audit_manager: TinyDBAuditManager):
        """
        Initialize audit log tool.
        
        Args:
            audit_manager: TinyDBAuditManager instance
        """
        super().__init__(
            "audit_log",
            "Log agent actions and events to audit system"
        )
        self.audit_manager = audit_manager
    
    def execute(
        self,
        workflow_id: str,
        execution_id: str,
        agent_name: str,
        action: str,
        status: str = "success",
        duration_ms: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an agent action.
        
        Args:
            workflow_id: Workflow identifier
            execution_id: Execution identifier
            agent_name: Agent name
            action: Action description
            status: Action status
            duration_ms: Action duration
            details: Additional details
            error: Error message if failed
            
        Returns:
            Result dictionary
        """
        try:
            self.audit_manager.log_agent_action(
                workflow_id=workflow_id,
                execution_id=execution_id,
                agent_name=agent_name,
                action=action,
                status=status,
                duration_ms=duration_ms,
                details=details,
                error=error
            )
            
            return {
                "success": True,
                "message": f"Action '{action}' logged for agent '{agent_name}'",
                "agent": agent_name,
                "action": action
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class WorkflowStatusTool(BaseTool):
    """
    Tool for tracking workflow status in audit system.
    
    Example:
        ```python
        tool = WorkflowStatusTool(audit_manager)
        
        # Start workflow
        exec_id = tool.execute(
            action="start",
            workflow_id="wf_123",
            user_id="user_1"
        )
        
        # End workflow
        tool.execute(
            action="end",
            workflow_id="wf_123",
            execution_id=exec_id,
            status="completed"
        )
        ```
    """
    
    def __init__(self, audit_manager: TinyDBAuditManager):
        """
        Initialize workflow status tool.
        
        Args:
            audit_manager: TinyDBAuditManager instance
        """
        super().__init__(
            "workflow_status",
            "Track workflow status in audit system"
        )
        self.audit_manager = audit_manager
    
    def execute(
        self,
        action: str,  # "start" or "end"
        workflow_id: str,
        execution_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        agents_used: Optional[List[str]] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track workflow status.
        
        Args:
            action: "start" or "end"
            workflow_id: Workflow identifier
            execution_id: Execution ID (required for "end")
            user_id: User ID (for "start")
            status: Final status (for "end")
            agents_used: List of agents used (for "end")
            error: Error message (for "end")
            
        Returns:
            Result dictionary
        """
        try:
            if action == "start":
                exec_id = self.audit_manager.start_workflow(
                    workflow_id=workflow_id,
                    user_id=user_id
                )
                
                return {
                    "success": True,
                    "message": "Workflow started",
                    "execution_id": exec_id,
                    "workflow_id": workflow_id
                }
            
            elif action == "end":
                if not execution_id:
                    return {"success": False, "error": "execution_id required for end action"}
                
                self.audit_manager.end_workflow(
                    workflow_id=workflow_id,
                    execution_id=execution_id,
                    status=status or "completed",
                    agents_used=agents_used,
                    error=error
                )
                
                return {
                    "success": True,
                    "message": "Workflow ended",
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "status": status or "completed"
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}


class AuditQueryTool(BaseTool):
    """
    Tool for querying audit data.
    
    Example:
        ```python
        tool = AuditQueryTool(audit_manager)
        
        # Get audit trail
        trail = tool.execute(
            query_type="audit_trail",
            workflow_id="wf_123"
        )
        
        # Get agent metrics
        metrics = tool.execute(query_type="agent_metrics")
        
        # Get statistics
        stats = tool.execute(query_type="statistics")
        ```
    """
    
    def __init__(self, audit_manager: TinyDBAuditManager):
        """
        Initialize audit query tool.
        
        Args:
            audit_manager: TinyDBAuditManager instance
        """
        super().__init__(
            "audit_query",
            "Query audit data and metrics"
        )
        self.audit_manager = audit_manager
    
    def execute(
        self,
        query_type: str,  # "audit_trail", "agent_metrics", "workflow_metrics", "statistics", "errors"
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query audit data.
        
        Args:
            query_type: Type of query
            workflow_id: Filter by workflow
            execution_id: Filter by execution
            agent_name: Filter by agent
            limit: Limit results
            
        Returns:
            Query results
        """
        try:
            if query_type == "audit_trail":
                results = self.audit_manager.get_audit_trail(
                    workflow_id=workflow_id,
                    execution_id=execution_id,
                    limit=limit
                )
                return {
                    "success": True,
                    "query_type": query_type,
                    "count": len(results),
                    "results": results
                }
            
            elif query_type == "agent_metrics":
                results = self.audit_manager.get_agent_metrics(agent_name=agent_name)
                return {
                    "success": True,
                    "query_type": query_type,
                    "count": len(results),
                    "results": results
                }
            
            elif query_type == "workflow_metrics":
                if not workflow_id:
                    return {"success": False, "error": "workflow_id required"}
                
                results = self.audit_manager.get_workflow_metrics(
                    workflow_id=workflow_id,
                    execution_id=execution_id
                )
                return {
                    "success": True,
                    "query_type": query_type,
                    "count": len(results),
                    "results": results
                }
            
            elif query_type == "statistics":
                stats = self.audit_manager.get_statistics()
                return {
                    "success": True,
                    "query_type": query_type,
                    "data": stats
                }
            
            elif query_type == "errors":
                results = self.audit_manager.get_recent_errors(limit=limit)
                return {
                    "success": True,
                    "query_type": query_type,
                    "count": len(results),
                    "results": results
                }
            
            else:
                return {"success": False, "error": f"Unknown query type: {query_type}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}


class ExportAuditTool(BaseTool):
    """
    Tool for exporting and managing audit data.
    
    Example:
        ```python
        tool = ExportAuditTool(audit_manager)
        
        # Export data
        result = tool.execute(
            action="export",
            export_path="audit_export.json"
        )
        
        # Clear old data
        result = tool.execute(
            action="clear_old",
            days=30
        )
        ```
    """
    
    def __init__(self, audit_manager: TinyDBAuditManager):
        """
        Initialize export audit tool.
        
        Args:
            audit_manager: TinyDBAuditManager instance
        """
        super().__init__(
            "export_audit",
            "Export and manage audit data"
        )
        self.audit_manager = audit_manager
    
    def execute(
        self,
        action: str,  # "export" or "clear_old"
        export_path: Optional[str] = None,
        days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Export or manage audit data.
        
        Args:
            action: "export" or "clear_old"
            export_path: Path to export to (for "export")
            days: Days to keep (for "clear_old")
            
        Returns:
            Result dictionary
        """
        try:
            if action == "export":
                if not export_path:
                    return {"success": False, "error": "export_path required"}
                
                self.audit_manager.export_data(export_path)
                
                return {
                    "success": True,
                    "message": f"Data exported to {export_path}",
                    "export_path": export_path
                }
            
            elif action == "clear_old":
                if days is None:
                    days = 30
                
                self.audit_manager.clear_old_data(days=days)
                
                return {
                    "success": True,
                    "message": f"Cleared data older than {days} days",
                    "days": days
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
