"""
TinyDB Audit System for Workflow Monitoring

This module provides persistent audit logging and workflow monitoring using TinyDB.
Features:
- Audit trail logging
- Workflow execution tracking
- Agent action recording
- Performance metrics
- Query and analysis capabilities

Author: AI Assistant
Date: 2024-11-27
"""

import json
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class AuditEntry:
    """Audit log entry"""
    timestamp: str
    event_type: str  # workflow_start, workflow_end, agent_action, error, etc.
    workflow_id: str
    execution_id: str
    agent_name: Optional[str] = None
    action: Optional[str] = None
    status: str = "success"
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class WorkflowAudit:
    """Workflow execution audit"""
    workflow_id: str
    execution_id: str
    user_id: Optional[str]
    start_time: str
    end_time: Optional[str]
    status: str  # completed, error, running, paused
    total_steps: int
    completed_steps: int
    agents_used: List[str]
    total_duration_ms: float
    error_details: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AgentMetrics:
    """Agent execution metrics"""
    agent_name: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_duration_ms: float
    total_duration_ms: float
    last_executed: str
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


# ============================================================================
# TinyDB Audit Manager
# ============================================================================

class TinyDBAuditManager:
    """
    Manages audit logging using TinyDB.
    
    Provides:
    - Centralized audit trail
    - Workflow tracking
    - Agent metrics
    - Query and analysis
    - Data persistence
    
    Example:
        ```python
        audit_mgr = TinyDBAuditManager()
        
        # Start workflow
        exec_id = audit_mgr.start_workflow("wf_123", "user_1")
        
        # Log agent action
        audit_mgr.log_agent_action(
            "wf_123", exec_id, "DataAnalyst",
            "analyze_csv", "success"
        )
        
        # End workflow
        audit_mgr.end_workflow("wf_123", exec_id, "completed")
        
        # Get metrics
        metrics = audit_mgr.get_workflow_metrics("wf_123", exec_id)
        ```
    """
    
    def __init__(self, db_path: str = "audit_logs"):
        """
        Initialize TinyDB Audit Manager.
        
        Args:
            db_path: Path to audit database directory
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # Initialize databases
        self.audit_db = TinyDB(str(self.db_path / "audit_log.json"))
        self.workflow_db = TinyDB(str(self.db_path / "workflows.json"))
        self.metrics_db = TinyDB(str(self.db_path / "metrics.json"))
        
        # Thread lock for concurrent access
        self._lock = threading.Lock()
    
    # ========================================================================
    # Workflow Management
    # ========================================================================
    
    def start_workflow(
        self,
        workflow_id: str,
        user_id: Optional[str] = None,
        total_steps: int = 0
    ) -> str:
        """
        Record workflow start.
        
        Args:
            workflow_id: Unique workflow identifier
            user_id: User who initiated workflow
            total_steps: Expected number of steps
            
        Returns:
            Execution ID
        """
        with self._lock:
            execution_id = f"exec_{int(datetime.now().timestamp() * 1000)}"
            start_time = datetime.now().isoformat()
            
            # Record in workflow DB
            workflow_audit = WorkflowAudit(
                workflow_id=workflow_id,
                execution_id=execution_id,
                user_id=user_id,
                start_time=start_time,
                end_time=None,
                status="running",
                total_steps=total_steps,
                completed_steps=0,
                agents_used=[],
                total_duration_ms=0.0
            )
            
            self.workflow_db.insert(workflow_audit.to_dict())
            
            # Record audit entry
            audit_entry = AuditEntry(
                timestamp=start_time,
                event_type="workflow_start",
                workflow_id=workflow_id,
                execution_id=execution_id,
                status="success",
                user_id=user_id,
                details={"total_steps": total_steps}
            )
            
            self.audit_db.insert(audit_entry.to_dict())
            
            return execution_id
    
    def end_workflow(
        self,
        workflow_id: str,
        execution_id: str,
        status: str = "completed",
        agents_used: Optional[List[str]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Record workflow completion.
        
        Args:
            workflow_id: Workflow identifier
            execution_id: Execution identifier
            status: Final status (completed, error, etc.)
            agents_used: List of agents used
            output_data: Final output data
            error: Error message if failed
        """
        with self._lock:
            end_time = datetime.now().isoformat()
            
            # Find and update workflow
            Workflow = Query()
            workflow = self.workflow_db.get(
                (Workflow.workflow_id == workflow_id) &
                (Workflow.execution_id == execution_id)
            )
            
            if workflow:
                # Calculate duration
                start = datetime.fromisoformat(workflow["start_time"])
                end = datetime.fromisoformat(end_time)
                duration_ms = (end - start).total_seconds() * 1000
                
                update_data = {
                    "end_time": end_time,
                    "status": status,
                    "total_duration_ms": duration_ms,
                    "agents_used": agents_used or [],
                    "output_data": output_data
                }
                
                if error:
                    update_data["error_details"] = error
                
                self.workflow_db.update(
                    update_data,
                    (Workflow.workflow_id == workflow_id) &
                    (Workflow.execution_id == execution_id)
                )
            
            # Record audit entry
            audit_entry = AuditEntry(
                timestamp=end_time,
                event_type="workflow_end",
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=status,
                details={"agents_used": agents_used or []}
            )
            
            if error:
                audit_entry.error_message = error
            
            self.audit_db.insert(audit_entry.to_dict())
    
    # ========================================================================
    # Agent Action Logging
    # ========================================================================
    
    def log_agent_action(
        self,
        workflow_id: str,
        execution_id: str,
        agent_name: str,
        action: str,
        status: str = "success",
        duration_ms: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Log an agent action.
        
        Args:
            workflow_id: Workflow identifier
            execution_id: Execution identifier
            agent_name: Name of agent
            action: Action performed
            status: Action status (success, error, etc.)
            duration_ms: Action duration in milliseconds
            details: Additional details
            error: Error message if failed
        """
        with self._lock:
            timestamp = datetime.now().isoformat()
            
            # Record audit entry
            audit_entry = AuditEntry(
                timestamp=timestamp,
                event_type="agent_action",
                workflow_id=workflow_id,
                execution_id=execution_id,
                agent_name=agent_name,
                action=action,
                status=status,
                duration_ms=duration_ms,
                details=details,
                error_message=error
            )
            
            self.audit_db.insert(audit_entry.to_dict())
            
            # Update agent metrics
            self._update_agent_metrics(agent_name, status, duration_ms, error)
    
    def _update_agent_metrics(
        self,
        agent_name: str,
        status: str,
        duration_ms: Optional[float],
        error: Optional[str]
    ):
        """Update agent execution metrics."""
        Metric = Query()
        existing = self.metrics_db.get(Metric.agent_name == agent_name)
        
        now = datetime.now().isoformat()
        
        if existing:
            # Update existing metrics
            updates = {
                "total_executions": existing["total_executions"] + 1,
                "last_executed": now
            }
            
            if status == "success":
                updates["successful_executions"] = existing["successful_executions"] + 1
            else:
                updates["failed_executions"] = existing["failed_executions"] + 1
                if error:
                    updates["last_error"] = error
            
            # Update average duration
            if duration_ms:
                total_duration = existing["total_duration_ms"] + duration_ms
                avg_duration = total_duration / updates["total_executions"]
                updates["avg_duration_ms"] = avg_duration
                updates["total_duration_ms"] = total_duration
            
            self.metrics_db.update(updates, Metric.agent_name == agent_name)
        
        else:
            # Create new metrics
            metrics = AgentMetrics(
                agent_name=agent_name,
                total_executions=1,
                successful_executions=1 if status == "success" else 0,
                failed_executions=0 if status == "success" else 1,
                avg_duration_ms=duration_ms or 0.0,
                total_duration_ms=duration_ms or 0.0,
                last_executed=now,
                last_error=error if status != "success" else None
            )
            
            self.metrics_db.insert(metrics.to_dict())
    
    # ========================================================================
    # Query and Analysis
    # ========================================================================
    
    def get_workflow_metrics(
        self,
        workflow_id: str,
        execution_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get workflow execution metrics.
        
        Args:
            workflow_id: Workflow identifier
            execution_id: Optional execution identifier
            
        Returns:
            List of workflow metrics
        """
        with self._lock:
            Workflow = Query()
            
            if execution_id:
                results = self.workflow_db.search(
                    (Workflow.workflow_id == workflow_id) &
                    (Workflow.execution_id == execution_id)
                )
            else:
                results = self.workflow_db.search(Workflow.workflow_id == workflow_id)
            
            return results
    
    def get_agent_metrics(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get agent performance metrics.
        
        Args:
            agent_name: Optional specific agent name
            
        Returns:
            Agent metrics
        """
        with self._lock:
            if agent_name:
                Metric = Query()
                results = self.metrics_db.search(Metric.agent_name == agent_name)
            else:
                results = self.metrics_db.all()
            
            return results
    
    def get_audit_trail(
        self,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail entries.
        
        Args:
            workflow_id: Filter by workflow
            execution_id: Filter by execution
            event_type: Filter by event type
            limit: Maximum entries to return
            
        Returns:
            List of audit entries
        """
        with self._lock:
            Audit = Query()
            query = None
            
            if workflow_id:
                query = Audit.workflow_id == workflow_id
            
            if execution_id:
                cond = Audit.execution_id == execution_id
                query = cond if query is None else (query & cond)
            
            if event_type:
                cond = Audit.event_type == event_type
                query = cond if query is None else (query & cond)
            
            if query is not None:
                results = self.audit_db.search(query)
            else:
                results = self.audit_db.all()
            
            # Sort by timestamp descending and limit
            results = sorted(results, key=lambda x: x["timestamp"], reverse=True)
            return results[-limit:]
    
    def get_recent_errors(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent errors from audit log.
        
        Args:
            hours: Look back this many hours
            limit: Maximum errors to return
            
        Returns:
            List of error entries
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=hours)
            Audit = Query()
            
            results = self.audit_db.search(
                (Audit.status == "error") &
                (Audit.timestamp >= cutoff.isoformat())
            )
            
            results = sorted(results, key=lambda x: x["timestamp"], reverse=True)
            return results[-limit:]
    
    def get_execution_summary(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary for a specific execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Execution summary
        """
        with self._lock:
            Workflow = Query()
            workflow = self.workflow_db.get(Workflow.execution_id == execution_id)
            
            if not workflow:
                return None
            
            # Get all audit entries for this execution
            Audit = Query()
            audits = self.audit_db.search(Audit.execution_id == execution_id)
            
            return {
                "workflow": workflow,
                "audit_entries": audits,
                "total_actions": len(audits),
                "agents_used": workflow.get("agents_used", [])
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            workflows = self.workflow_db.all()
            audits = self.audit_db.all()
            metrics = self.metrics_db.all()
            
            completed = sum(1 for w in workflows if w.get("status") == "completed")
            errors = sum(1 for w in workflows if w.get("status") == "error")
            
            return {
                "total_workflows": len(workflows),
                "completed_workflows": completed,
                "failed_workflows": errors,
                "success_rate": (completed / len(workflows) * 100) if workflows else 0,
                "total_audit_entries": len(audits),
                "total_agents": len(metrics),
                "agent_metrics": metrics
            }
    
    # ========================================================================
    # Data Management
    # ========================================================================
    
    def clear_old_data(self, days: int = 30):
        """
        Clear data older than specified days.
        
        Args:
            days: Clear data older than this many days
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(days=days)
            cutoff_iso = cutoff.isoformat()
            
            # Clear from workflow DB
            Workflow = Query()
            self.workflow_db.remove(Workflow.start_time < cutoff_iso)
            
            # Clear from audit DB
            Audit = Query()
            self.audit_db.remove(Audit.timestamp < cutoff_iso)
    
    def export_data(self, export_path: str):
        """
        Export all audit data to JSON file.
        
        Args:
            export_path: Path to export to
        """
        with self._lock:
            export_data = {
                "workflows": self.workflow_db.all(),
                "audits": self.audit_db.all(),
                "metrics": self.metrics_db.all(),
                "export_time": datetime.now().isoformat()
            }
            
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)
    
    def close(self):
        """Close all databases."""
        self.audit_db.close()
        self.workflow_db.close()
        self.metrics_db.close()
