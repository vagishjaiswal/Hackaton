"""
Test Suite for TinyDB Audit System

Comprehensive tests for:
- Audit manager
- Audit tools
- Integration with agents

Run with: pytest tests/test_audit_system.py -v

Author: AI Assistant
Date: 2024-11-27
"""

import pytest
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.audit_manager import (
    TinyDBAuditManager,
    AuditEntry,
    WorkflowAudit,
    AgentMetrics
)
from src.tools.audit_tools import (
    AuditLogTool,
    WorkflowStatusTool,
    AuditQueryTool,
    ExportAuditTool
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def audit_manager():
    """Create test audit manager"""
    manager = TinyDBAuditManager(db_path="test_audit_db")
    yield manager
    # Cleanup
    manager.close()
    # Remove test database
    import shutil
    if Path("test_audit_db").exists():
        shutil.rmtree("test_audit_db")


@pytest.fixture
def audit_tools(audit_manager):
    """Create audit tools"""
    return {
        "log": AuditLogTool(audit_manager),
        "workflow": WorkflowStatusTool(audit_manager),
        "query": AuditQueryTool(audit_manager),
        "export": ExportAuditTool(audit_manager)
    }


# ============================================================================
# Test Audit Manager
# ============================================================================

class TestAuditManager:
    """Test audit manager functionality"""
    
    def test_initialization(self, audit_manager):
        """Test audit manager initialization"""
        assert audit_manager.audit_db is not None
        assert audit_manager.workflow_db is not None
        assert audit_manager.metrics_db is not None
    
    def test_start_workflow(self, audit_manager):
        """Test starting a workflow"""
        exec_id = audit_manager.start_workflow("test_wf", user_id="user1")
        
        assert exec_id.startswith("exec_")
        
        # Verify in database
        workflow = audit_manager.get_workflow_metrics("test_wf")
        assert len(workflow) > 0
        assert workflow[0]["status"] == "running"
    
    def test_end_workflow(self, audit_manager):
        """Test ending a workflow"""
        exec_id = audit_manager.start_workflow("test_wf")
        audit_manager.end_workflow("test_wf", exec_id, "completed")
        
        # Verify
        workflow = audit_manager.get_workflow_metrics("test_wf", exec_id)
        assert len(workflow) > 0
        assert workflow[0]["status"] == "completed"
        assert workflow[0]["end_time"] is not None
    
    def test_log_agent_action(self, audit_manager):
        """Test logging agent action"""
        exec_id = audit_manager.start_workflow("test_wf")
        
        audit_manager.log_agent_action(
            workflow_id="test_wf",
            execution_id=exec_id,
            agent_name="TestAgent",
            action="test_action",
            status="success",
            duration_ms=100.0
        )
        
        # Verify
        trail = audit_manager.get_audit_trail(workflow_id="test_wf")
        assert len(trail) > 0
        
        actions = [e for e in trail if e["event_type"] == "agent_action"]
        assert len(actions) > 0
        assert actions[0]["agent_name"] == "TestAgent"
    
    def test_get_agent_metrics(self, audit_manager):
        """Test getting agent metrics"""
        exec_id = audit_manager.start_workflow("test_wf")
        
        # Log multiple actions
        for i in range(3):
            audit_manager.log_agent_action(
                workflow_id="test_wf",
                execution_id=exec_id,
                agent_name="TestAgent",
                action=f"action_{i}",
                duration_ms=100.0
            )
        
        # Get metrics
        metrics = audit_manager.get_agent_metrics("TestAgent")
        assert len(metrics) > 0
        assert metrics[0]["agent_name"] == "TestAgent"
        assert metrics[0]["total_executions"] == 3
        assert metrics[0]["successful_executions"] == 3
    
    def test_get_audit_trail(self, audit_manager):
        """Test getting audit trail"""
        exec_id = audit_manager.start_workflow("test_wf")
        
        audit_manager.log_agent_action(
            workflow_id="test_wf",
            execution_id=exec_id,
            agent_name="TestAgent",
            action="test"
        )
        
        # Get trail
        trail = audit_manager.get_audit_trail(workflow_id="test_wf")
        assert len(trail) > 0
    
    def test_get_recent_errors(self, audit_manager):
        """Test getting recent errors"""
        exec_id = audit_manager.start_workflow("test_wf")
        
        # Log error
        audit_manager.log_agent_action(
            workflow_id="test_wf",
            execution_id=exec_id,
            agent_name="TestAgent",
            action="test",
            status="error",
            error="Test error"
        )
        
        # Get errors
        errors = audit_manager.get_recent_errors(hours=24)
        assert len(errors) > 0
    
    def test_get_execution_summary(self, audit_manager):
        """Test getting execution summary"""
        exec_id = audit_manager.start_workflow("test_wf")
        
        audit_manager.log_agent_action(
            workflow_id="test_wf",
            execution_id=exec_id,
            agent_name="Agent1",
            action="action1"
        )
        
        summary = audit_manager.get_execution_summary(exec_id)
        assert summary is not None
        assert summary["workflow"]["execution_id"] == exec_id
    
    def test_get_statistics(self, audit_manager):
        """Test getting overall statistics"""
        # Create a few workflows
        for i in range(3):
            exec_id = audit_manager.start_workflow(f"wf_{i}")
            audit_manager.end_workflow(f"wf_{i}", exec_id, "completed")
        
        # Get stats
        stats = audit_manager.get_statistics()
        assert stats["total_workflows"] >= 3
        assert stats["completed_workflows"] >= 3
    
    def test_clear_old_data(self, audit_manager):
        """Test clearing old data"""
        exec_id = audit_manager.start_workflow("test_wf")
        audit_manager.end_workflow("test_wf", exec_id, "completed")
        
        # Should not delete recent data
        audit_manager.clear_old_data(days=1)
        
        workflows = audit_manager.get_workflow_metrics("test_wf")
        assert len(workflows) > 0
    
    def test_export_data(self, audit_manager):
        """Test exporting data"""
        exec_id = audit_manager.start_workflow("test_wf")
        audit_manager.log_agent_action("test_wf", exec_id, "Agent", "action")
        audit_manager.end_workflow("test_wf", exec_id, "completed")
        
        # Export
        export_file = "test_export.json"
        audit_manager.export_data(export_file)
        
        # Verify file exists and has data
        assert Path(export_file).exists()
        
        with open(export_file, 'r') as f:
            data = json.load(f)
            assert "workflows" in data
            assert "audits" in data
        
        # Cleanup
        Path(export_file).unlink()


# ============================================================================
# Test Audit Tools
# ============================================================================

class TestAuditTools:
    """Test audit tools"""
    
    def test_audit_log_tool(self, audit_tools, audit_manager):
        """Test audit log tool"""
        exec_id = audit_manager.start_workflow("test_wf")
        
        result = audit_tools["log"].execute(
            workflow_id="test_wf",
            execution_id=exec_id,
            agent_name="TestAgent",
            action="test_action",
            status="success"
        )
        
        assert result["success"] is True
    
    def test_workflow_status_tool_start(self, audit_tools):
        """Test workflow status tool - start"""
        result = audit_tools["workflow"].execute(
            action="start",
            workflow_id="test_wf",
            user_id="user1"
        )
        
        assert result["success"] is True
        assert "execution_id" in result
    
    def test_workflow_status_tool_end(self, audit_tools, audit_manager):
        """Test workflow status tool - end"""
        exec_id = audit_manager.start_workflow("test_wf")
        
        result = audit_tools["workflow"].execute(
            action="end",
            workflow_id="test_wf",
            execution_id=exec_id,
            status="completed"
        )
        
        assert result["success"] is True
    
    def test_audit_query_tool_audit_trail(self, audit_tools, audit_manager):
        """Test audit query tool - audit trail"""
        exec_id = audit_manager.start_workflow("test_wf")
        audit_manager.log_agent_action("test_wf", exec_id, "Agent", "action")
        
        result = audit_tools["query"].execute(
            query_type="audit_trail",
            workflow_id="test_wf"
        )
        
        assert result["success"] is True
        assert result["query_type"] == "audit_trail"
    
    def test_audit_query_tool_agent_metrics(self, audit_tools, audit_manager):
        """Test audit query tool - agent metrics"""
        exec_id = audit_manager.start_workflow("test_wf")
        audit_manager.log_agent_action("test_wf", exec_id, "Agent", "action")
        
        result = audit_tools["query"].execute(
            query_type="agent_metrics"
        )
        
        assert result["success"] is True
    
    def test_audit_query_tool_statistics(self, audit_tools, audit_manager):
        """Test audit query tool - statistics"""
        exec_id = audit_manager.start_workflow("test_wf")
        audit_manager.end_workflow("test_wf", exec_id, "completed")
        
        result = audit_tools["query"].execute(
            query_type="statistics"
        )
        
        assert result["success"] is True
        assert "data" in result
    
    def test_export_audit_tool(self, audit_tools, audit_manager):
        """Test export audit tool"""
        exec_id = audit_manager.start_workflow("test_wf")
        audit_manager.end_workflow("test_wf", exec_id, "completed")
        
        export_file = "test_tool_export.json"
        
        result = audit_tools["export"].execute(
            action="export",
            export_path=export_file
        )
        
        assert result["success"] is True
        assert Path(export_file).exists()
        
        # Cleanup
        Path(export_file).unlink()


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests"""
    
    def test_complete_workflow_with_tools(self, audit_manager, audit_tools):
        """Test complete workflow using tools"""
        # Start workflow
        result = audit_tools["workflow"].execute(
            action="start",
            workflow_id="integration_test",
            user_id="user1"
        )
        exec_id = result["execution_id"]
        
        # Log actions from multiple agents
        for agent in ["Agent1", "Agent2", "Agent3"]:
            audit_tools["log"].execute(
                workflow_id="integration_test",
                execution_id=exec_id,
                agent_name=agent,
                action=f"action_by_{agent}",
                status="success",
                duration_ms=100.0
            )
        
        # End workflow
        result = audit_tools["workflow"].execute(
            action="end",
            workflow_id="integration_test",
            execution_id=exec_id,
            status="completed",
            agents_used=["Agent1", "Agent2", "Agent3"]
        )
        
        assert result["success"] is True
        
        # Query results
        summary = audit_manager.get_execution_summary(exec_id)
        assert summary is not None
        assert len(summary["audit_entries"]) >= 5  # start + 3 actions + end
        assert summary["workflow"]["status"] == "completed"
    
    def test_error_handling_workflow(self, audit_manager, audit_tools):
        """Test error handling in workflow"""
        exec_id = audit_manager.start_workflow("error_test")
        
        # Log error
        audit_tools["log"].execute(
            workflow_id="error_test",
            execution_id=exec_id,
            agent_name="Agent",
            action="failed_action",
            status="error",
            error="Something went wrong"
        )
        
        # End with error
        audit_tools["workflow"].execute(
            action="end",
            workflow_id="error_test",
            execution_id=exec_id,
            status="error",
            error="Workflow failed"
        )
        
        # Verify
        summary = audit_manager.get_execution_summary(exec_id)
        assert summary["workflow"]["status"] == "error"
        
        errors = audit_manager.get_recent_errors(hours=24)
        assert len(errors) > 0


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance tests"""
    
    def test_high_volume_logging(self, audit_manager):
        """Test high volume logging"""
        exec_id = audit_manager.start_workflow("perf_test", total_steps=1000)
        
        start = time.time()
        
        # Log 1000 actions
        for i in range(1000):
            audit_manager.log_agent_action(
                workflow_id="perf_test",
                execution_id=exec_id,
                agent_name="Agent",
                action=f"action_{i}",
                duration_ms=10.0
            )
        
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 30  # 30 seconds for 1000 logs
        
        audit_manager.end_workflow("perf_test", exec_id, "completed")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
